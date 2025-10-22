import os
import json
import pathlib
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    flash
)
from dotenv import load_dotenv
from perplexity import Perplexity
from search import search_topic
from database import *

# Loads environment variables from a .env file
load_dotenv()

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY")

# Sets up database
create_db()

BASE_PATH = pathlib.Path(__file__).parent
pdfs_dir = BASE_PATH / "static/pdfs"

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

@app.context_processor
def inject_user():
    uid = session.get('user_id')
    return {
        "logged_in": bool(uid),
        "username": (get_username(uid) if uid else None),
    }

# Home page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        print(request.form)
    return render_template("index.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_id = validate_user(username, password)
        if user_id:
            session['user_id'] = user_id
            flash("Login successful", "success")
            return jsonify({"status": "success", "message": "Login successful."})
        else:
            flash("Invalid credentials", "error")
            return jsonify({"status": "error", "message": "Invalid credentials."}), 401
    return render_template("login.html")

# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        if add_user(email, username, password):
            return jsonify({"status": "success", "message": "Registration successful."})
        else:
            return jsonify({"status": "error", "message": "Registration failed. Email may already be in use."}), 400
    return render_template("register.html")

# Logout
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully", "success")
    return jsonify({"status": "success", "message": "Logged out successfully."})

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

    try:
        if 'user_id' in session:
            user_id = session['user_id']
            add_learning_packet(
                user_id,
                main_topic,
                subtopics,
                grade_level,
                exercise_count,
                pdf_path
            )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error saving learning packet: {str(e)}"}), 500

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

# List user's generated PDFs in the list view
@app.route("/list_user", methods=["POST"])
def list_pdfs():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Login to view your files"}), 401

    user_id = session['user_id']
    packets = get_user_learning_packets(user_id)  
    items = []
    for packet in packets:
        fname = pathlib.Path(packet['pdf_path']).name
        items.append({
            "id": packet["id"],
            "filename": fname,
            "name": f"{packet['topic']} ({packet['grade_level']})",
            "is_public": bool(packet["public"]),
        })
    return jsonify({"status": "success", "items": items})

# Lists public PDFs
@app.route("/list_public", methods=["GET"])
def list_public_pdfs():
    packets = get_all_public_learning_packets()
    items = []
    for packet in packets:
        fname = pathlib.Path(packet['pdf_path']).name
        items.append({
            "id": packet["id"],
            "filename": fname,
            "name": f"{packet['topic']} by {get_username(packet['user_id'])} ({packet['grade_level']})"
        })
    return jsonify({"status": "success", "items": items})

# Update packet visibility
@app.route("/update_visibility", methods=["GET", "POST"])
def update_visibility():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Login to save your file and update its visibility"}), 401

    try:
        packet_id = int(request.form.get("packet_id"))
        is_public = int(request.form.get("is_public"))  # 0 or 1
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid parameters."}), 400
    
    if not packet_id or is_public is None:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    # Verify ownership
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM learning_packets WHERE id = ?", (packet_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "Packet not found."}), 404
    if row["user_id"] != session['user_id']:
        return jsonify({"status": "error", "message": "Not authorized."}), 403

    update_packet_visibility(packet_id, is_public)  # <- your DB helper
    return jsonify({"status": "success", "message": "Packet visibility updated."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
