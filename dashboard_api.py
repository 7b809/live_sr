from fastapi import FastAPI
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from fastapi.responses import HTMLResponse

app = FastAPI()

client = MongoClient(MONGO_URI)
col = client[DB_NAME][COLLECTION_NAME]


@app.get("/ui")
def ui():
    with open("dashboard.html") as f:
        return HTMLResponse(f.read())
    
@app.get("/signals")
def get_signals():
    data = list(col.find({}, {"_id": 0}).sort("time", -1).limit(100))
    return data


@app.get("/")
def home():
    return {"status": "running"}