#!/usr/bin/env python3
import os, json, datetime, threading
from flask import Flask, render_template, send_from_directory, jsonify

SCRIPT_PATH = "/Volumes/lev/Documents/code/scripts/auto_screenshot.sh"
SCREENSHOT_BASE = "/Volumes/lev/doclev/Screenshots"
LOG_FILE = "/Volumes/lev/Documents/code/scripts/screenshot_log.json"
INTERVAL_MIN = 15
START_HOUR, END_HOUR = 8, 22

app = Flask(__name__, template_folder="templates")


def find_latest_screenshot():
    latest_file, latest_time = None, 0
    for root, _, files in os.walk(SCREENSHOT_BASE):
        for f in files:
            if f.lower().endswith((".png", ".jpg")):
                path = os.path.join(root, f)
                t = os.path.getmtime(path)
                if t > latest_time:
                    latest_file, latest_time = path, t
    return latest_file


def run_screenshot():
    now = datetime.datetime.now()
    hour = now.strftime("%Y-%m-%d %H")
    minute = now.strftime("%H:%M:%S")
    os.system(f"bash '{SCRIPT_PATH}'")
    latest_file = find_latest_screenshot()
    if not latest_file:
        print("⚠️ No screenshot found!")
        return
    data = json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else {}
    data.setdefault(hour, []).append({"time": minute, "file": latest_file})
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Logged screenshot at {minute}")


def schedule_loop():
    now = datetime.datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        run_screenshot()
    threading.Timer(INTERVAL_MIN * 60, schedule_loop).start()


threading.Thread(target=schedule_loop, daemon=True).start()


@app.route("/")
def index():
    data = json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else {}
    return render_template("index.html", logs=data)


@app.route("/preview/<int:idx>/<hour>")
def preview(idx, hour):
    if not os.path.exists(LOG_FILE):
        return "No log", 404
    data = json.load(open(LOG_FILE))
    entry = data.get(hour, [])[idx]
    file_path = entry.get("file")
    if file_path and os.path.exists(file_path):
        dirpath, filename = os.path.split(file_path)
        return send_from_directory(dirpath, filename)
    return "File not found", 404


@app.route("/shot", methods=["POST"])
def shot_now():
    run_screenshot()
    return jsonify(
        {"status": "ok", "time": datetime.datetime.now().strftime("%H:%M:%S")}
    )


if __name__ == "__main__":
    print(
        f"✅ Screenshot monitor running between {START_HOUR}:00–{END_HOUR}:00, every {INTERVAL_MIN} min"
    )
    app.run(host="127.0.0.1", port=5000)
