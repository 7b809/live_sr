from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, BASE_WS_URL, SECURITIES

# 🔥 IMPORT ENGINE
from core.engine import TradingEngine
from core.ws_client import WSClient

import threading

app = FastAPI()

# ---------------- Mongo ----------------
client = MongoClient(MONGO_URI)
col = client[DB_NAME][COLLECTION_NAME]

# ---------------- Engine Instance ----------------
engine = TradingEngine()


# ---------------- BACKGROUND ENGINE ----------------
def start_engine():
    print("🚀 Starting Trading Engine (background)...")

    for sec in SECURITIES:
        print(f"🔌 Connecting WS: {sec}")
        WSClient(BASE_WS_URL, sec, engine.on_tick).start()

    print("✅ Engine started successfully")


@app.on_event("startup")
def startup_event():
    # run engine in background thread
    thread = threading.Thread(target=start_engine)
    thread.daemon = True
    thread.start()


# ---------------- API ----------------
@app.get("/signals")
def get_signals():
    data = list(col.find({}, {"_id": 0}).sort("time", -1).limit(100))
    return data


@app.get("/ui")
def ui():
    with open("dashboard.html") as f:
        return HTMLResponse(f.read())


@app.get("/")
def root():
    return {"status": "running"}