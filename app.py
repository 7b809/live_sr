from core.engine import TradingEngine
from core.ws_client import WSClient
from config import *
import time

engine = TradingEngine()

for sec in SECURITIES:
    WSClient(BASE_WS_URL, sec, engine.on_tick).start()

print("🚀 Running full SR engine...")

while True:
    time.sleep(1)