from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:Hololab_1005@dialogflow-t.fzgrvjs.mongodb.net/"
client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)

db = client["dialogflow_t"]
orders = db["kfc_order_data"]

def save_cx_order(order):
    orders.insert_one(order)
    print("CX order saved:", order)
