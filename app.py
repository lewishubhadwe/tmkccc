# language: Python, file: app.py, runtime: Python 3.10+
import os
import time
import threading
import random
import requests
from flask import Flask, request, jsonify, render_template_string
from instagrapi import Client

app = Flask(__name__)

# --- SYNC MECHANISM ---
SYNC_LOCK = threading.Lock()
TURN_LOCK = threading.Lock()
CURRENT_TURN = 0
TOTAL_THREADS = 0

STATE = {
    "total_sent": 0,
    "live_accounts": 0,
    "sessions": [],
    "target": "",
    "gc_link": "",
    "delay": 5.5,
    "is_running": False,
    "logs": []
}

try:
    with open("index.html", "r", encoding="utf-8") as f:
        HTML_TEMPLATE = f.read()
except Exception:
    HTML_TEMPLATE = "<h1>index.html missing</h1>"

# --- FULL PAYLOAD DATA ---
PAYLOAD_LIST = [
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝙰𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💚 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🩵 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🖤 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🤍 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  ❤️ \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  🧡 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💛 \n \n \n",
    "{target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n    {target} 𝙇𝙀𝙒𝙄𝙎 𝘽𝘼𝙰𝙋 𝘽𝙊𝙇 𝙍𝙉𝘿𝙔𝙆𝙀 ➬  💜 \n \n \n"
]

def log_msg(msg):
    timestamp = time.strftime("%H:%M:%S")
    STATE["logs"].append(f"[{timestamp}] {msg}")
    if len(STATE["logs"]) > 100:
        STATE["logs"].pop(0)

# --- KEEP ALIVE ---
def keep_alive():
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        return
    while True:
        time.sleep(300)
        try:
            requests.get(url, timeout=15)
        except Exception:
            pass

if not any(t.name == "KeepAlive" for t in threading.enumerate()):
    t = threading.Thread(target=keep_alive, name="KeepAlive", daemon=True)
    t.start()

# --- WORKER FOR EACH SESSION ---
def session_worker(session_data, thread_id, my_index):
    global CURRENT_TURN
    cl = Client()
    if session_data.get('proxy'):
        cl.set_proxy(session_data['proxy'])
    
    try:
        cl.login_by_sessionid(session_data["session_id"])
        log_msg(f"✅ Thread Started: @{session_data['username']}")
    except Exception as e:
        log_msg(f"❌ Auth failed for @{session_data['username']}: {str(e)[:30]}")
        return

    uname = session_data['username']
    
    while STATE["is_running"]:
        # --- SYNC LOGIC ---
        # Wait until it's this thread's turn to send
        while True:
            with TURN_LOCK:
                if CURRENT_TURN == my_index:
                    break
            time.sleep(0.01)

        template = random.choice(PAYLOAD_LIST)
        payload_text = template.format(target=STATE['target'])
        
        try:
            cl.direct_send(payload_text, thread_ids=[thread_id])
            STATE["total_sent"] += 1
            current_delay = float(STATE.get("delay", 5.5))
            log_msg(f"📨 @{uname} sent payload. Next in {current_delay}s.")
        except Exception as e:
            log_msg(f"❌ @{uname} failed: {str(e)[:40]}")
            if "login_required" in str(e).lower() or "challenge" in str(e).lower():
                log_msg(f"⚠️ @{uname} session invalid. Thread stopping.")
                break
        
        # --- SYNC UPDATE ---
        with TURN_LOCK:
            CURRENT_TURN += 1
            if CURRENT_TURN >= TOTAL_THREADS:
                CURRENT_TURN = 0

        time.sleep(0.1) # 0.1 second gap between threads firing
        time.sleep(current_delay)

# --- SPAM ENGINE MASTER ---
def spam_master():
    global TOTAL_THREADS, CURRENT_TURN
    
    log_msg("🔥 Spam Engine Started (Simultaneous Mode)")
    
    try:
        raw_id = STATE['gc_link'].split('/t/')[-1].replace('/', '').split('?')[0]
        thread_id = str(raw_id).strip()
    except:
        log_msg("❌ Invalid GC Link. Stopping.")
        STATE['is_running'] = False
        return

    if not STATE["sessions"]:
        log_msg("❌ No sessions found.")
        STATE["is_running"] = False
        return

    with TURN_LOCK:
        TOTAL_THREADS = len(STATE["sessions"])
        CURRENT_TURN = 0

    for i, s in enumerate(STATE["sessions"]):
        t = threading.Thread(target=session_worker, args=(s, thread_id, i), daemon=True)
        t.start()

    while STATE["is_running"]:
        time.sleep(1)

    log_msg("🛑 Spam Engine Stopped")

# --- ROUTES ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/state', methods=['GET'])
def get_state():
    STATE["live_accounts"] = len(STATE["sessions"])
    return jsonify(STATE)

@app.route('/api/session', methods=['POST'])
def add_session():
    data = request.json
    sid = data.get('session_id', '').strip().replace('"', '').replace("'", "")
    proxy = data.get('proxy', '').strip()
    
    if sid.startswith("sessionid="):
        sid = sid.replace("sessionid=", "")
    
    if not sid:
        return jsonify({"error": "Empty session"}), 400
    if any(s["session_id"] == sid for s in STATE["sessions"]):
        return jsonify({"error": "Session already added"}), 400

    try:
        cl = Client()
        if proxy:
            cl.set_proxy(proxy)
            
        cl.login_by_sessionid(sid)
        uname = cl.username
        
        STATE["sessions"].append({
            "session_id": sid, 
            "username": uname,
            "proxy": proxy
        })
        log_msg(f"✅ Authenticated: @{uname}")
        return jsonify({"status": "ok", "username": uname})
    except Exception as e:
        log_msg(f"❌ Auth failed: {str(e)[:30]}")
        return jsonify({"error": f"Auth failed: {str(e)[:40]}"}), 400

@app.route('/api/session/<sid>', methods=['DELETE'])
def remove_session(sid):
    STATE['sessions'] = [s for s in STATE['sessions'] if s["session_id"] != sid]
    return jsonify({"status": "ok"})

@app.route('/api/config', methods=['POST'])
def update_config():
    data = request.json
    STATE['target'] = data.get('target', STATE['target'])
    STATE['gc_link'] = data.get('gc_link', STATE['gc_link'])
    
    if 'delay' in data:
        try:
            STATE['delay'] = float(data['delay'])
        except ValueError:
            pass
            
    return jsonify({"status": "ok"})

@app.route('/api/toggle', methods=['POST'])
def toggle_spam():
    data = request.json
    
    if data.get('running') and not STATE['sessions']:
        return jsonify({"error": "No sessions added"}), 400
    if data.get('running') and (not STATE['gc_link'] or not STATE['target']):
        return jsonify({"error": "Missing GC Link or Target"}), 400
        
    STATE['is_running'] = data.get('running', False)
    
    if STATE['is_running']:
        t = threading.Thread(target=spam_master, daemon=True)
        t.start()
    else:
        log_msg("Stopping engine...")
        
    return jsonify({"status": "ok", "is_running": STATE['is_running']})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)