from flask import Flask, request, render_template, send_file
import urllib.request
from urllib.parse import urlparse
import tempfile
import json
import os

app = Flask(__name__)

def extract_id(url):
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2 or parts[-2] != "share":
        raise ValueError("Invalid Loom share URL format.")
    return parts[-1]

def fetch_loom_download_url(loom_id):
    print(f"[INFO] Fetching download URL for Loom ID: {loom_id}")
    req = urllib.request.Request(
        url=f"https://www.loom.com/api/campaigns/sessions/{loom_id}/transcoded-url",
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data["url"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        loom_url = request.form.get("loom_url", "").strip()
        print(f"[INFO] Received Loom URL: {loom_url}")

        try:
            loom_id = extract_id(loom_url)
            video_url = fetch_loom_download_url(loom_id)

            print(f"[INFO] Downloading video from: {video_url}")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            urllib.request.urlretrieve(video_url, temp_file.name)

            print(f"[INFO] Sending file to browser.")
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=f"{loom_id}.mp4"
            )

        except Exception as e:
            print(f"[ERROR] {e}")
            return render_template("index.html", error=str(e)), 500

    return render_template("index.html", error=None)

# Important for deployment to Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)