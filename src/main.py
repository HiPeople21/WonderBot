import random
import os
import sqlite3
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    jsonify,
    send_from_directory,
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("PPLX_API_KEY")

<<<<<<< HEAD
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("home.html")
=======
>>>>>>> 2688b4f9a498fef2b7e0d5e9190b6c0d2e73567f

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
