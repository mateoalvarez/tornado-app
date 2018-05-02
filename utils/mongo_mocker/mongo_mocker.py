from pymongo import MongoClient
import os
import time


mongo_client = MongoClient(host=os.environ.get("MONGO_HOST", "192.168.240.3"), port=int(os.environ.get("MONGO_PORT", "27017")))
mongo_database = mongo_client[os.environ.get("MONGO_DBNAME", "pyxis_db")]
collection = mongo_database["mock_collection"]

values = [1, 1, 2, 1, 0, -1, 0, 1, 2, 3, 4, 5, 4, 3, 2, 2, 2, 2, 2, 1, 0, -1, -2, -3, -4, -3, -2, -1, 0, 1, 2, 3, 4]


for i in values:
    record = {"aggregated": i, "timestamp": time.time(), "tweet_text": "tweet number - {index}".format(index = values.index(i))}
    record_inserted_id = collection.insert_one(record).inserted_id
    print ("Record ID: {record_id}".format(record_id=record_inserted_id))
