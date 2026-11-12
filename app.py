from flask import Flask, request, send_file
import imageio_ffmpeg
import subprocess
import tempfile
import os
import re
import zipfile

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        video = request.files.get("video")
        permission = request.form.get("permission")

        if not video or not video.filename:
            message = "Please select a video."
        elif permission != "yes":
            message = "Please confirm video permission."
        else:
            try:
                folder = tempfile.mkdtemp()
                input_file = os.path.join(folder, "input.mp4")
                video.save(input_file)

                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

                result = subprocess.run(
                    [ffmpeg, "-i", input_file],
                    capture_output=True, text=True
                )

                match = re.search(
                    r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)",
                    result.stderr
                )

                if not match:
                    raise Exception("Video duration not found")

                h, m, s = match.groups()
                duration = int(h) * 3600 + int(m) * 60 + float(s)

                if duration < 30:
                    raise Exception("Video must be at least 30 seconds")

                clip_length = duration / 30
                zip_path = os.path.join(folder, "JATIN_CLIPS.zip")

                with zipfile.ZipFile(zip_path, "w") as archive:
                    for i in range(30):
                        start = i * clip_length
                        output = os.path.join(folder, f"clip_{i+1}.mp4")

                        subprocess.run([
                            ffmpeg, "-y",
                            "-ss", str(start),
                            "-i", input_file,
                            "-t", str(clip_length),
                            "-c", "copy",
                            output
                        ], check=True, capture_output=True)

                        archive.write(output, f"clip_{i+1}.mp4")

                return send_file(
                    zip_path,
                    as_attachment=True,
                    download_name="JATIN_AI_CLIPS.zip"
                )

            except Exception:
                message = "Processing failed. Try a smaller video."

    return """
    <html>
    <head>
    <title>JATIN AI CLIPPER</title>
    </head>
    <body style="background:#080808;color:white;text-align:center;padding:35px;font-family:Arial;">
    <h1>JATIN AI CLIPPER</h1>
    <h3>Turn Long Videos Into Shorts</h3>
    <form method="POST" enctype="multipart/form-data">
    <input type="file" name="video" accept="video/*" required>
    <br><br>
    <label>
    <input type="checkbox" name="permission" value="yes" required>
    I own this video or have permission to use it.
    </label>
    <br><br>
    <button style="padding:15px;">GENERATE 30 CLIPS</button>
    </form>
    <p style="color:lime;">""" + message + """</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()
