#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================
# Shotline+ : 自动读取截图目录并网页显示时间线（分小时）
# ======================================================

from flask import Flask, render_template, send_from_directory, abort
import os
from collections import defaultdict
import subprocess, datetime, threading, time
import random

app = Flask(__name__)

SCREENSHOT_BASE = "/Volumes/lev/doclev/Screenshots"
SCRIPT_PATH = "/Volumes/lev/Documents/code/scripts/Shotline/auto_screenshot.sh"


def trigger_screenshot():
    """执行截图脚本"""
    try:
        subprocess.run(["/bin/bash", SCRIPT_PATH], check=True)
        print("✅ 手动或定时截图任务执行完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 截图脚本执行失败: {e}")


def schedule_screenshot():
    """每天8:00~22:00之间 每小时随机触发4次截图"""
    while True:
        now = datetime.datetime.now()
        if 8 <= now.hour < 22:
            # 当前小时内随机生成4个触发秒数点
            triggers = sorted(random.sample(range(0, 3600), 1))
            start = time.time()

            for t in triggers:
                target = start + t
                delay = target - time.time()
                if delay > 0:
                    time.sleep(delay)
                if not (8 <= datetime.datetime.now().hour < 22):
                    break
                trigger_screenshot()

        # 每天 03:00 执行一次清理（用 last_deletion_date 避免同小时内多次运行）
        now = datetime.datetime.now()
        if now.hour == 3:
            today = now.date()
            if last_deletion_date != today:
                cutoff = now - datetime.timedelta(days=7)
                for d in os.listdir(SCREENSHOT_BASE):
                    full = os.path.join(SCREENSHOT_BASE, d)
                    if os.path.isdir(full):
                        try:
                            dt = datetime.datetime.strptime(d, "%Y-%m-%d")
                            if dt < cutoff:
                                shutil.rmtree(full)
                        except ValueError:
                            pass
                last_deletion_date = today

        # 避免紧循环（短睡眠确保上面的 03:00 检测能在小时内多次循环中仅触发一次）
        else:
            # 非时段内，每隔10分钟再检查
            time.sleep(600)


@app.route("/")
@app.route("/<date>")
def index(date=None):
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")

    day_path = os.path.join(SCREENSHOT_BASE, date)
    grouped = defaultdict(list)

    files = []

    if os.path.exists(day_path):
        files = [
            f
            for f in os.listdir(day_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

    # 按小时和时间名（文件名升序）分组
    for f in sorted(files):
        hour = f[:2] if len(f) >= 2 and f[2] == "-" else "??"
        grouped[hour].append(f)

    # 每小时内也升序
    for h in grouped:
        grouped[h].sort()

    # return render_template(
    #     "index.html",
    #     date=date,
    #     shots_by_hour=sorted(grouped.items(), reverse=True),
    #     available_dates=list_dirs(),
    # )
    return render_template(
        "index.html",
        date=date,
        shots_by_hour=[(h, grouped[h]) for h in sorted(grouped.keys())],  # 小时升序
        available_dates=sorted(list_dirs(), reverse=True),  # 日期降序（最近在上面）
    )


@app.route("/screenshots/<date>/<filename>")
def serve_screenshot(date, filename):
    dir_path = os.path.join(SCREENSHOT_BASE, date)
    if not os.path.exists(os.path.join(dir_path, filename)):
        abort(404)
    return send_from_directory(dir_path, filename)


@app.route("/trigger_shot", methods=["POST"])
def trigger_shot():
    threading.Thread(target=trigger_screenshot, daemon=True).start()
    return "OK", 200


def list_dirs():
    dirs = []
    for d in os.listdir(SCREENSHOT_BASE):
        if os.path.isdir(os.path.join(SCREENSHOT_BASE, d)) and d.startswith("20"):
            dirs.append(d)
    return sorted(dirs, reverse=True)


if __name__ == "__main__":
    threading.Thread(target=schedule_screenshot, daemon=True).start()
    app.run(debug=True, use_reloader=False, port=55050, host="0.0.0.0")
