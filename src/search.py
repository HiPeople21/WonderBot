import random
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from perplexity import Perplexity
import subprocess
import json
from urllib.parse import urlencode, quote

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_SECRET_KEY = os.getenv("AMADEUS_SECRET_KEY")
FLIGHT_SOURCES = os.getenv("FLIGHT_SOURCES", "").split(",")

client = Perplexity()

# ------------------------- link helpers -------------------------

def kayak_link(origin, destination, depart_date, return_date=None, adults=1, cabin="economy", currency="USD"):
    # https://www.kayak.com/flights/ORIG-DEST/DEPART[/RETURN]?sort=price_a&fs=cabin=e&adults=2&cc=USD
    cabin_map = {"economy":"e","premium":"p","business":"b","first":"f"}
    base = f"https://www.kayak.com/flights/{origin}-{destination}/{depart_date}"
    if return_date:
        base += f"/{return_date}"
    qs = f"?sort=price_a&fs=cabin={cabin_map.get(cabin.lower(),'e')}&adults={adults}&cc={currency}"
    return base + qs

# ------------------------- small utilities -------------------------

AMAD_CABIN = {
    "economy": "ECONOMY",
    "premium": "PREMIUM_ECONOMY",
    "business": "BUSINESS",
    "first": "FIRST",
}

def _iso_to_date(iso_str: str) -> str:
    # accepts "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM"
    d = iso_str.split("T", 1)[0]
    datetime.strptime(d, "%Y-%m-%d")  # validate
    return d

# Minimal IATA mapping for common cities (extend as needed)
IATA_CITY = {
    "london": "LON", "tokyo": "TYO", "new york": "NYC", "los angeles": "LAX",
    "paris": "PAR", "singapore": "SIN", "hong kong": "HKG"
}

def _to_iata(s: str) -> str:
    if not s:
        return s
    s = s.strip()
    if len(s) == 3 and s.isalpha():
        return s.upper()
    return IATA_CITY.get(s.lower(), s.upper())  # fallback: return upper as-is

# ------------------------- main function -------------------------

def find_flights(departure_city, arrival_city, departure_datetime, return_date, budget, currency='$',
                 passengers=1, cabin_class="economy"):
    """
    Searches Amadeus (via curl/subprocess), returns structured offers with:
    - price, validating airline, legs (with flight numbers),
    - and corresponding link to book.
    """

    # ---- OAuth token
    token_cmd = [
        "curl", "-s", "-X", "POST",
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "-d", f"grant_type=client_credentials&client_id={AMADEUS_API_KEY}&client_secret={AMADEUS_SECRET_KEY}"
    ]
    token_out = subprocess.run(token_cmd, capture_output=True, text=True)
    access_token = json.loads(token_out.stdout)["access_token"]

    # ---- Inputs → Amadeus params
    origin = _to_iata(departure_city)     # accept IATA or city
    destination = _to_iata(arrival_city)  # accept IATA or city
    depart_date = _iso_to_date(departure_datetime)
    ret_date = _iso_to_date(return_date) if return_date else None
    adults = int(passengers)
    currency_code = "USD"  # keep USD for hackathon simplicity
    travel_class = AMAD_CABIN.get(cabin_class.lower(), "ECONOMY")
    max_results = 10

    # ---- Flight Offers search (subprocess curl)
    base_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    q = (
        f"?originLocationCode={origin}"
        f"&destinationLocationCode={destination}"
        f"&departureDate={depart_date}"
        f"{f'&returnDate={ret_date}' if ret_date else ''}"
        f"&adults={adults}"
        f"&currencyCode={currency_code}"
        f"&travelClass={travel_class}"
        f"&max={max_results}"
    )
    result_cmd = [
        "curl", "-s", "-X", "GET", base_url + q,
        "-H", f"Authorization: Bearer {access_token}"
    ]
    result = subprocess.run(result_cmd, capture_output=True, text=True)

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON from Amadeus", "raw": result.stdout}

    data = payload.get("data", [])
    dicts = payload.get("dictionaries", {})
    carriers = dicts.get("carriers", {})
    aircraft = dicts.get("aircraft", {})

    items = []
    for offer in data:
        price_total = float(offer["price"]["grandTotal"])
        validating = (offer.get("validatingAirlineCodes") or [None])[0]
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            continue

        # determine O&D / dates from first itinerary
        out_segments = itineraries[0].get("segments", [])
        if not out_segments:
            continue
        o_iata = out_segments[0]["departure"]["iataCode"]
        d_iata = out_segments[-1]["arrival"]["iataCode"]
        d_date = out_segments[0]["departure"]["at"][:10]

        r_date = None
        if len(itineraries) > 1 and itineraries[1].get("segments"):
            r_date = itineraries[1]["segments"][0]["departure"]["at"][:10]

        # legs with flight numbers
        legs = []
        for itin in itineraries:
            segs = []
            for s in itin.get("segments", []):
                cc = s["carrierCode"]
                segs.append({
                    "from": s["departure"]["iataCode"],
                    "to": s["arrival"]["iataCode"],
                    "depart": s["departure"]["at"],
                    "arrive": s["arrival"]["at"],
                    "carrier": carriers.get(cc, cc),
                    "flight_number": f"{cc}{s['number']}",
                    "aircraft": aircraft.get(s["aircraft"]["code"], s["aircraft"]["code"]),
                    "stops": s.get("numberOfStops", 0),
                })
            legs.append(segs)

        # builds kayak link
        link_ky = kayak_link(o_iata, d_iata, d_date, r_date, adults=adults, cabin=cabin_class, currency=currency_code)

        items.append({
            "price_total": price_total,
            "currency": offer["price"]["currency"],
            "validating_airline": carriers.get(validating, validating),
            "origin": o_iata,
            "destination": d_iata,
            "depart_date": d_date,
            "return_date": r_date,
            "link": link_ky,
            "itinerary": legs,
            "raw_id": offer.get("id"),
        })

    items.sort(key=lambda x: x["price_total"])
    return items

# ---- Example call (kept from your script) ------------------------------------
# results = find_flights("LHR", "HND", "2025-11-03T05:00", "2025-11-07T16:00", 10000, passengers=2)
# for r in results[:3]:
#     print(f"${r['price_total']} | {r['origin']}→{r['destination']} {r['depart_date']}")
#     print("KY :", r["link"])
#     print()

# Make the API call
# completion = client.chat.completions.create(
#     model="sonar-pro",
#     messages=[
#         {"role": "user", "content": "https://www.kayak.com/flights/LHR-HND/2025-11-03/2025-11-07?sort=price_a&fs=cabin%3De&adults=2&cc=USD&attempt=1&lastms=1760739758128 what flights are on this page and what are their prices"}
#     ]
# )

# # Print the AI's response
# print(completion.choices[0].message.content)

import requests

# API configuration
API_URL = "https://api.perplexity.ai/chat/completions"

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "content-type": "application/json"
}

# Query that benefits from search classifier
user_query = '''
You are a helpful AI assistant.

Rules:
1. Provide only the final answer. It is important that you do not include any explanation on the steps below.
2. Do not show the intermediate steps information.

Steps:
1. Make sure the price is within the budget.
2. Make sure to return relevant flight details in structured format.
3. Make sure all of the flight info satisfies my prompt.
4. You do not need to return the link to book the flight, the most important thing to get right is the price and flight number.
4. Return the answer in the following format:
   1. Price with currency symbol.
   2. Date and time of departure and arrival.
   3. Airline name and flight number.
   4. If the flight requires a layover, include the layover city and duration.
   
Question: What flights can I get from London to Tokyo departing on November 3, 2025 for 2 adults in economy class within a budget of $2,000?'''

payload = {
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": user_query}],
    "stream": False,
}

response = requests.post(API_URL, json=payload, headers=headers)
for result in response.json()['search_results']:
    print(result)
    print()