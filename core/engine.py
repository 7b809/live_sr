import json
from datetime import datetime
from core.candle_builder import CandleBuilder
from core.indicator import SRIndicator
from config import *

# 🔥 NEW: MongoDB
from pymongo import MongoClient


class TradingEngine:
    def __init__(self):
        # ---------------- LOAD DATA ----------------
        self.data = self.load_history()

        # ---------------- CORE ----------------
        self.builder = CandleBuilder(TIMEFRAME_MINUTES)

        self.indicator = SRIndicator(
            LOOKBACK,
            VOL_LEN,
            ATR_PERIOD,
            BOX_WIDTH_MULT
        )

        # ---------------- MONGODB ----------------
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.col = self.db[COLLECTION_NAME]

        # 🔒 prevent duplicates
        try:
            self.col.create_index(
                [("time", 1), ("type", 1)],
                unique=True
            )
        except:
            pass

        print("✅ Trading Engine Initialized")
        print(f"📊 Loaded candles: {len(self.data)}")

    # ---------------- LOAD HISTORY ----------------
    def load_history(self):
        try:
            with open(DATA_FILE) as f:
                d = json.load(f)

            for x in d:
                x["time"] = datetime.fromisoformat(x["time"])

            return d

        except Exception as e:
            print("❌ Failed to load history:", e)
            return []

    # ---------------- SAVE SIGNAL ----------------
    def save_signal(self, signal):
        try:
            doc = {
                "signal": signal["signal"],
                "type": signal["type"],
                "price": float(signal["price"]),
                "time": signal["time"].isoformat(),
                "created_at": datetime.utcnow()
            }

            self.col.insert_one(doc)
            print("💾 Saved to MongoDB:", doc)

        except Exception as e:
            # ignore duplicate key errors
            if "duplicate key" not in str(e):
                print("❌ Mongo Error:", e)

    # ---------------- MAIN TICK HANDLER ----------------
    def on_tick(self, tick):
        try:
            # ---------------- PARSE TICK ----------------
            price = float(tick.get("LTP", 0))
            volume = float(tick.get("volume", 1))  # fallback
            ts = datetime.now()

            if price == 0:
                return

            # ---------------- BUILD CANDLE ----------------
            candle = self.builder.update(price, volume, ts)

            # ---------------- NEW CANDLE ----------------
            if candle:
                self.data.append(candle)

                print(f"\n🕯 New Candle: {candle}")

                # ---------------- RUN INDICATOR ----------------
                signals = self.indicator.run(self.data)

                if signals:
                    last = signals[-1]

                    print("🚨 SIGNAL:", last)

                    # ---------------- SAVE ----------------
                    self.save_signal(last)

                else:
                    print("ℹ️ No signal this candle")

        except Exception as e:
            print("❌ ENGINE ERROR:", e)