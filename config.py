import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "trading")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "signals")
BASE_WS_URL = os.getenv("BASE_WS_URL")
TIMEFRAME_MINUTES = int(os.getenv("TIMEFRAME_MINUTES", 5))
LOOKBACK = int(os.getenv("LOOKBACK", 20))

SECURITIES = ["51"]   # start with one (NIFTY-like)

VOL_LEN = 2
ATR_PERIOD = 200
BOX_WIDTH_MULT = 1

DATA_FILE = "data/output.json"