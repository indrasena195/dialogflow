from google.cloud import dialogflow_v2 as dialogflow
from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:Hololab_1005@dialogflow-t.fzgrvjs.mongodb.net/"
client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)
db = client["dialogflow_t"]
orders = db["es_order_data"]

order_info = {
        "name": "",
        "phone": "",
        "order_type": "",
        "food_type": "",
        "pizza_size": "",
        "pizza_toppings": "",
    }

def clean_params(params):
    clean = {}
    for key, value in params.items():
        if hasattr(value, "__iter__") and not isinstance(value, str):
            clean[key] = list(value)
        else:
            clean[key] = value
    return clean

def detect_intent_es(project_id, text, language_code="en"):
    session_id = "test-session"
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    print("Query text:", response.query_result.query_text)
    print("Detected intent:", response.query_result.intent.display_name)
    print("Fulfillment text:", response.query_result.fulfillment_text)

    raw_params = dict(response.query_result.parameters)
    params = clean_params(raw_params)
    print("Parameters:", params)
    if "ordertype" in params:
        if len(params["ordertype"]) > 0:
            order_info["order_type"] = params["ordertype"][-1]

    if "food-type" in params:
        if len(params["food-type"]) > 0:
            order_info["food_type"] = params["food-type"][-1]

    if "pizza-size" in params:
        if len(params["pizza-size"]) > 0:
            order_info["pizza_size"] = params["pizza-size"][-1]

    if "pizza-toppings" in params:
        if len(params["pizza-toppings"]) > 0:
            order_info["pizza_toppings"] = ", ".join(params["pizza-toppings"])

    if "given-name" in params:
        if len(params["given-name"]) > 0:
            order_info["name"] = params["given-name"][-1]

    if "phone-number" in params:
        if len(params["phone-number"]) > 0:
            order_info["phone"] = params["phone-number"][-1]

    if response.query_result.intent.display_name == "customer_info":
        orders.insert_one(order_info)
        print("Order saved to MongoDB!")

    return response.query_result.fulfillment_text
