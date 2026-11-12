from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>JATIN AI CLIPPER</title>
    </head>
    <body style="background:#080808;color:white;text-align:center;padding:40px;font-family:Arial;">
        <h1>JATIN AI CLIPPER</h1>
        <h3>Turn Long Videos Into Shorts</h3>
        <input placeholder="Paste YouTube Link" style="padding:15px;width:80%;">
        <br><br>
        <button style="padding:15px;">GENERATE CLIPS</button>
        <p>1080p Full HD</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()
