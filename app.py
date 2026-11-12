
from flask import Flask, send_file, request, render_template_string
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

@app.route("/generate", methods=["POST"])
def generate():
    video_url = request.form.get("video_url", "").strip()
    clip_count = request.form.get("clip_count", "1")
    duration = request.form.get("duration", "60")
    subtitles = request.form.get("subtitles", "english")

    if not video_url:
        return "Please enter a video link.", 400

    if not video_url.startswith(("https://", "http://")):
        return "Please enter a valid video URL.", 400

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>JATIN AI CLIPPER</title>
    <style>
    body { background:#080808; color:white; font-family:Arial;
           text-align:center; padding:30px; }
    .box { background:#151515; padding:25px; border-radius:15px;
           max-width:500px; margin:40px auto; }
    h2 { color:#ff3030; }
    p { color:#ccc; line-height:1.6; }
    a { color:#ff5555; }
    </style>
    </head>
    <body>
    <div class="box">
    <h2>Request Received!</h2>
    <p>Your video link has been received.</p>
    <p>Requested clips: {{ count }}</p>
    <p>Duration: {{ duration }} seconds</p>
    <p>Subtitles: {{ subtitles }}</p>
    <p><b>Video processing is not connected yet.</b></p>
    <a href="/">Go Back</a>
    </div>
    </body>
    </html>
    """, count=clip_count, duration=duration, subtitles=subtitles)

if __name__ == "__main__":
    app.run()
