
from flask import Flask, send_file, request, render_template_string
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

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
    video_file = request.files.get("video_file")

    clip_count = request.form.get("clip_count", "1")
    duration = request.form.get("duration", "60")
    subtitles = request.form.get("subtitles", "english")

    has_file = video_file and video_file.filename

    if bool(video_url) == bool(has_file):
        return "Please provide either a YouTube link OR an MP4 file.", 400

    if video_url:
        if not video_url.startswith(("https://", "http://")):
            return "Please enter a valid video URL.", 400
        source_message = "Video link received successfully."

    else:
        filename = secure_filename(video_file.filename)

        if not filename.lower().endswith(".mp4"):
            return "Only MP4 files are allowed.", 400

        saved_name = str(uuid.uuid4()) + ".mp4"
        save_path = os.path.join(UPLOAD_DIR, saved_name)
        video_file.save(save_path)

        source_message = "MP4 video uploaded successfully."

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>JATIN AI CLIPPER</title>
    <style>
    body {
        background:#080808;
        color:white;
        font-family:Arial;
        text-align:center;
        padding:30px;
    }
    .box {
        background:#151515;
        padding:25px;
        border-radius:15px;
        max-width:500px;
        margin:40px auto;
    }
    h2 { color:#ff3030; }
    p { color:#ccc; line-height:1.6; }
    a { color:#ff5555; }
    </style>
    </head>
    <body>
    <div class="box">
    <h2>Request Received!</h2>
    <p>{{ source }}</p>
    <p>Requested clips: {{ count }}</p>
    <p>Duration: {{ duration }} seconds</p>
    <p>Subtitles: {{ subtitles }}</p>
    <p><b>Actual clip generation is the next step.</b></p>
    <a href="/">Go Back</a>
    </div>
    </body>
    </html>
    """, source=source_message, count=clip_count,
         duration=duration, subtitles=subtitles)

@app.errorhandler(413)
def file_too_large(error):
    return "Video is too large. Maximum upload size is 100 MB.", 413

if __name__ == "__main__":
    app.run()
