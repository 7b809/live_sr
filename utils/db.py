from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

class MongoDB:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.col = self.db[COLLECTION_NAME]

    def insert_signal(self, signal):
        try:
            self.col.insert_one(signal)
            print("💾 Saved to MongoDB")
        except Exception as e:
            print("Mongo Error:", e)