from pymongo import MongoClient
import os
import datetime


mongo_client = MongoClient(host=os.environ.get("MONGO_HOST", "192.168.240.3"), port=int(os.environ.get("MONGO_PORT", "27017")))
mongo_database = mongo_client[os.environ.get("MONGO_DBNAME", "pyxis_db")]
collection = mongo_database["test_collection_order"]
"""
primero = collection.insert_one({"orden": "primero"}).inserted_id
segundo = collection.insert_one({"orden": "segundo"}).inserted_id
tercero = collection.insert_one({"orden": "tercero"}).inserted_id
cuarto = collection.insert_one({"orden": "cuarto"}).inserted_id

print(primero)
print(segundo)
print(tercero)
print(cuarto)
"""

a = list(collection.find().sort([("_id", -1)]).limit(1))
if len(a) == 0:
    print("empty")
else:
    print("not empty")

print(a[0]["orden"])
"""
for doc in a:
    print(doc)
"""
"""
for i in values:
    record = {"aggregated": i, "timestamp": datetime.datetime.now(), "tweet_text": "tweet number - {index}".format(index = values.index(i))}
    record_inserted_id = collection.insert_one(record).inserted_id
    print ("Record ID: {record_id}".format(record_id=record_inserted_id))
"""

USER_DB = "user_1"
USER_COLLECTION = "application_3"

PYXIS_CLASS = "pyxis-classification"
PYXIS_AGGR = "aggregated"
CREATED_AT = "created_at"


import dateutil.parser
import datetime

element = mongo_client["malaas_tested_db"]["malaas_tested_collection"].find_one()

mongo_client[USER_DB][USER_COLLECTION].drop()

element[PYXIS_CLASS] = -1
element[PYXIS_AGGR] = -1
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,5)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)

print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)

element[PYXIS_CLASS] = -1
element[PYXIS_AGGR] = -2
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,6)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)

print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = -1
element[PYXIS_AGGR] = -3
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,7)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = -1
element[PYXIS_AGGR] = -4
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,8)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = -1
element[PYXIS_AGGR] = -5
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,9)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = -4
element.pop("_id", None)
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,10)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = -3
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,11)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = -2
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = -1
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,12)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = 0
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,13)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = -1
element[PYXIS_AGGR] = -1
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,14)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = 0
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,15)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = 1
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = 2
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,16)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)

element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = 3
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,18)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)

element[PYXIS_CLASS] = 1
element[PYXIS_AGGR] = 4
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,19)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)


element[PYXIS_CLASS] = -1
element[PYXIS_AGGR] = 3
tweet_date = dateutil.parser.parse(element[CREATED_AT]) + datetime.timedelta(0,20)
element[CREATED_AT] = tweet_date.strftime('%a %b %d %H:%M:%S %z %Y')
element.pop("_id", None)
print(mongo_client[USER_DB][USER_COLLECTION].insert_one(element).inserted_id)
