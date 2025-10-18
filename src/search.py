import os, json, requests
from dotenv import load_dotenv
load_dotenv()

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

def _json_sanitize(s: str):
    try:
        return json.loads(s)
    except Exception:
        for a,b in [("{","}"),("[","]")]:
            i, j = s.find(a), s.rfind(b)
            if i != -1 and j != -1 and j > i:
                try: return json.loads(s[i:j+1])
                except Exception: pass
    return None

def _assert_api_key():
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY.strip() == "":
        raise RuntimeError("PERPLEXITY_API_KEY is missing or empty")

def _call_perplexity(messages, *, temperature=0.2, max_tokens=8000, debug=True):
    _assert_api_key()
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": "sonar-pro",                # try "sonar" if you get 400 / access errors
        "messages": messages,
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": max_tokens,            # raise cap to reduce truncation
        "stream": False,
        "enable_search_classifier": True,
        "return_search_results": False,
    }
    try:
        r = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=90)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HTTP request failed: {e}")

    if debug:
        print(f"[perplexity] status={r.status_code}")
        # print only first 800 chars to avoid flooding logs
        print(f"[perplexity] body head: {r.text[:800]}")

    # Explicitly raise HTTP errors so you see body in console
    try:
        r.raise_for_status()
    except requests.HTTPError as he:
        raise RuntimeError(f"API error {r.status_code}: {r.text}") from he

    data = r.json()
    # Defensive: ensure choices exist
    if not isinstance(data, dict) or "choices" not in data or not data["choices"]:
        raise RuntimeError(f"Unexpected response structure: {json.dumps(data)[:800]}")
    content = data["choices"][0].get("message", {}).get("content", "")
    if not content:
        raise RuntimeError(f"No content returned: {json.dumps(data)[:800]}")
    return content

# ---------------- textbook generator (uses the robust caller) ----------------

_SCHEMA_HINT = {
    "type": "object",
    "required": ["title","learning_path","sections","summary","estimated_total_read_time_minutes"],
    "properties": {
        "title": {"type":"string"},
        "learning_path": {"type":"array","items":{"type":"string"}},
        "sections": {
            "type":"array",
            "items":{
                "type":"object",
                "required":[
                    "title","overview","key_points","formulas",
                    "diagram","worked_example","common_pitfalls","mini_quiz"
                ],
                "properties":{
                    "title":{"type":"string"},
                    "overview":{"type":"string"},
                    "key_points":{"type":"array","items":{"type":"string"}},
                    "formulas":{"type":"array","items":{"type":"string"}},
                    "derivations":{"type":"string"},
                    "diagram":{"type":"object","required":["caption","instructions"],
                               "properties":{"caption":{"type":"string"},"instructions":{"type":"string"}}},
                    "worked_example":{"type":"object","required":["prompt","steps","answer"],
                                      "properties":{"prompt":{"type":"string"},
                                                    "steps":{"type":"array","items":{"type":"string"}},
                                                    "answer":{"type":"string"}}},
                    "common_pitfalls":{"type":"array","items":{"type":"string"}},
                    "mini_quiz":{"type":"array","items":{"type":"object","required":["q","a"],
                                  "properties":{"q":{"type":"string"},"a":{"type":"string"}}}}
                }
            }
        },
        "summary":{"type":"string"},
        "estimated_total_read_time_minutes":{"type":"integer"}
    }
}

_SYSTEM_MSG = (
    "You are a master educator. Write like a concise textbook: clean, precise, structured. "
    "Short paragraphs (plain text), minimal jargon, clear notation. "
    "No citations, links, or markdown. Return ONLY valid JSON."
)

def find_textbook_packet(topic: str, subtopics: list[str], grade_level: str,
                         max_sections: int = 6, quiz_per_section: int = 3, debug=True) -> dict:
    subtopics_txt = ", ".join(subtopics) if subtopics else "—"
    user_msg = f"""
Create a condensed, concise textbook-style packet for a {grade_level} student.

Primary topic: "{topic}"
Focus subtopics (include and integrate): {subtopics_txt}

Constraints and style:
- Clarity and density. Short paragraphs (plain text), precise definitions, minimal fluff.
- Logical learning order (prerequisites first).
- Each section: 120–220 word overview, 3–6 key points, essential formulas (LaTeX ok),
  1 worked example with steps, 1 small diagram described by text (caption + drawing instructions),
  2–4 common pitfalls, and {quiz_per_section} mini-quiz Q/A.
- Keep derivations brief (5–10 lines) only when essential.
- DO NOT include citations, URLs, references, or markdown.
- Keep total number of sections ≤ {max_sections} by merging closely related subtopics.

Output:
Return ONLY valid JSON matching this schema (no prose outside JSON):
{json.dumps(_SCHEMA_HINT)}
""".strip()

    content = _call_perplexity(
        [{"role": "system", "content": _SYSTEM_MSG},
         {"role": "user", "content": user_msg}],
        max_tokens=8000,
        debug=debug
    )
    parsed = _json_sanitize(content)
    if not parsed:
        # fail-soft: small skeleton so downstream doesn’t crash
        return {
            "title": f"{topic} — Learning Packet",
            "learning_path": subtopics or [topic],
            "sections": [{
                "title":"Overview",
                "overview":"Content unavailable due to JSON parse or token limit.",
                "key_points":[],
                "formulas":[],
                "derivations":"",
                "diagram":{"caption":"—","instructions":"—"},
                "worked_example":{"prompt":"—","steps":[],"answer":"—"},
                "common_pitfalls":[],
                "mini_quiz":[]
            }],
            "summary":"Generation failed softly; check API logs.",
            "estimated_total_read_time_minutes": 3
        }
    return parsed

def textbook_json_to_markdown(packet: dict) -> str:
    md = [f"# {packet.get('title','Learning Packet')}\n"]
    md.append(f"**Estimated reading time:** {packet.get('estimated_total_read_time_minutes','~')} minutes\n")
    lp = packet.get("learning_path") or []
    if lp: md.append("**Learning order:** " + " → ".join(lp) + "\n")
    for section in packet.get("sections", []):
        md.append(f"## {section.get('title','Section')}\n")
        if section.get("overview"): md.append(section["overview"] + "\n")
        if section.get("key_points"):
            md.append("**Key points:**")
            for p in section["key_points"]: md.append(f"- {p}")
        if section.get("formulas"):
            md.append("**Formulas:**")
            for f in section["formulas"]: md.append(f"- `{f}`")
        if section.get("derivations"):
            md.append("**Sketch derivation:**"); md.append(section["derivations"])
        if section.get("worked_example"):
            ex = section["worked_example"]; md.append("\n**Worked Example:**")
            if ex.get("prompt"): md.append(f"*{ex['prompt']}*")
            for step in ex.get("steps", []): md.append(f"  - {step}")
            if ex.get("answer"): md.append(f"**Answer:** {ex['answer']}\n")
        if section.get("diagram"):
            d = section["diagram"]; md.append("**Diagram:** " + d.get("caption",""))
            if d.get("instructions"): md.append("Instructions: " + d["instructions"])
        if section.get("common_pitfalls"):
            md.append("**Common Pitfalls:**")
            for p in section["common_pitfalls"]: md.append(f"- {p}")
        if section.get("mini_quiz"):
            md.append("**Quick Quiz:**")
            for qa in section["mini_quiz"]:
                md.append(f"- {qa.get('q','')}  \n  **Ans:** {qa.get('a','')}")
        md.append("\n---\n")
    if packet.get("summary"): md.append("## Summary\n" + packet["summary"])
    return "\n".join(md)

# ---------------- quick smoke test ----------------
if __name__ == "__main__":
    try:
        pkt = find_textbook_packet(
            topic="Vectors",
            subtopics=["Gram-Schmidt process", "Vector spaces"],
            grade_level="undergraduate",
            max_sections=6,
            quiz_per_section=3,
            debug=True     # prints HTTP status and body head
        )
        md = textbook_json_to_markdown(pkt)
        print(md)
    except Exception as e:
        print("\n[FATAL]", e)
