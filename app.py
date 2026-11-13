
from flask import Flask, send_file, request, render_template_string, url_for
from werkzeug.utils import secure_filename
from moviepy import VideoFileClip
import os
import uuid

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


@app.route("/")
def home():
    return send_file(
        os.path.join(BASE_DIR, "templates", "Templates", "index.html")
    )


@app.route("/admin")
def admin():
    return send_file(os.path.join(BASE_DIR, "admin.html"))


@app.route("/health")
def health():
    return "JATIN AI CLIPPER is running!"


@app.route("/download/<filename>")
def download(filename):
    safe_name = secure_filename(filename)
    file_path = os.path.join(OUTPUT_DIR, safe_name)

    if not os.path.isfile(file_path):
        return "Clip not found.", 404

    return send_file(file_path, as_attachment=True)


@app.route("/generate", methods=["POST"])
def generate():
    video_url = request.form.get("video_url", "").strip()
    video_file = request.files.get("video_file")

    try:
        clip_count = int(request.form.get("clip_count", "1"))
        duration = int(request.form.get("duration", "60"))
    except ValueError:
        return "Invalid clip settings.", 400

    subtitles = request.form.get("subtitles", "english")
    has_file = video_file and video_file.filename

    if bool(video_url) == bool(has_file):
        return "Please provide either a YouTube link OR an MP4 file.", 400

    if not 1 <= clip_count <= 30 or not 1 <= duration <= 180:
        return "Invalid clip count or duration.", 400

    if video_url:
        return "YouTube link received. Direct YouTube processing is not enabled yet.", 400

    filename = secure_filename(video_file.filename)

    if not filename.lower().endswith(".mp4"):
        return "Only MP4 files are allowed.", 400

    job_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, job_id + ".mp4")
    video_file.save(input_path)

    generated_clips = []

    try:
        with VideoFileClip(input_path) as video:
            total_duration = video.duration

            if total_duration < duration:
                return "Video is shorter than the requested clip duration.", 400

            if total_duration < clip_count * duration:
                return "Video is too short for the requested number of clips.", 400

            available_space = total_duration - duration

            for i in range(clip_count):
                if clip_count == 1:
                    start_time = 0
                else:
                    start_time = available_space * i / (clip_count - 1)

                end_time = start_time + duration
                output_name = f"{job_id}_clip_{i + 1}.mp4"
                output_path = os.path.join(OUTPUT_DIR, output_name)

                clip = video.subclipped(start_time, end_time)

                try:
                    clip.write_videofile(
                        output_path,
                        codec="libx264",
                        audio_codec="aac",
                        logger=None
                    )
                finally:
                    clip.close()

                generated_clips.append(output_name)

    except Exception:
        return "Video processing failed. Try a smaller MP4 video.", 500

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>JATIN AI CLIPPER</title>
    <style>
    body {
        background: #080808;
        color: white;
        font-family: Arial;
        text-align: center;
        padding: 20px;
    }
    .box {
        background: #151515;
        padding: 25px;
        border-radius: 15px;
        max-width: 500px;
        margin: 30px auto;
    }
    h2 { color: #ff3030; }
    a {
        display: block;
        background: #ff3030;
        color: white;
        padding: 13px;
        margin: 12px;
        border-radius: 8px;
        text-decoration: none;
    }
    </style>
    </head>
    <body>
    <div class="box">
    <h2>Clips Generated!</h2>
    <p>Total clips: {{ clips|length }}</p>
    {% for clip in clips %}
    <a href="{{ url_for('download', filename=clip) }}">
    Download Clip {{ loop.index }} MP4
    </a>
    {% endfor %}
    <a href="/">Go Back</a>
    </div>
    </body>
    </html>
    """, clips=generated_clips)


@app.errorhandler(413)
def file_too_large(error):
    return "Video is too large. Maximum upload size is 100 MB.", 413


if __name__ == "__main__":
    app.run()
