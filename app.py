from flask import Flask, send_file
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def home():
    return send_file(os.path.join(BASE_DIR, "templates", "Templates", "index.html"))

@app.route("/admin")
def admin():
    return send_file(os.path.join(BASE_DIR, "admin.html"))

@app.route("/health")
def health():
    return "JATIN AI CLIPPER is running!"

if __name__ == "__main__":
    app.run()
