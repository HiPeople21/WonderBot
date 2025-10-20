import os
import json
import pathlib
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
)
from dotenv import load_dotenv
from perplexity import Perplexity
from search import search_topic

# Loads environment variables from a .env file
load_dotenv()

BASE_PATH = pathlib.Path(__file__).parent
pdfs_dir = BASE_PATH / "static/pdfs"

app = Flask(
    __name__,
    static_folder="static",
)
API_KEY = os.getenv("PPLX_API_KEY")

# Breaks down a sentence into main topic and subtopics
def breakdown_topics(sentence):
    """
    Uses Perplexity's Sonar-Pro model to extract a main topic and subtopics
    from a sentence describing what a student wants to learn.
    Example:
        breakdown_topics("I want to learn about vector spaces, gram schmidt, and matrix operations")
    """
    client = Perplexity()

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {
                "role": "system",
                "content": "Extract a student's learning intent into a main topic and subtopics. Respond ONLY in JSON.",
            },
            {"role": "user", "content": f'Break this down: "{sentence}"'},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "main_topic": {"type": "string"},
                        "subtopics": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["main_topic", "subtopics"],
                }
            },
        },
        temperature=0.2,
        max_tokens=1000,
    )

    content = response.choices[0].message.content
    return json.loads(content)

# Home page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        print(request.form)
    return render_template("index.html")

# Create a learning packet
@app.route("/create", methods=["POST"])
def create():
    guide_prompt = request.form.get("guide-prompt")
    exercise_count = int(request.form.get("exercise-count", 5))
    grade_level = request.form.get("grade-level")

    topics = breakdown_topics(guide_prompt)
    main_topic = topics["main_topic"]
    subtopics = topics["subtopics"]

    # Generate the learning packet
    pdf_path = search_topic(main_topic, subtopics, grade_level, exercise_count)

    # Return JSON so the frontend can handle it directly
    return jsonify(
        {
            "status": "success",
            "message": "Learning packet created successfully.",
            "pdf_path": pdf_path,
            "main_topic": main_topic,
            "subtopics": subtopics,
        }
    )

# List already generated PDFs in the list view
@app.route("/list", methods=["POST"])
def list_pdfs():
    """Lists already generated PDFs"""
    return jsonify([str(i.relative_to(pdfs_dir)) for i in pdfs_dir.rglob("*.pdf")])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
