from google.cloud import dialogflowcx_v3beta1 as dialogflowcx
from db_cx import save_cx_order

def extract_cx_params(parameters):
    if not parameters:
        return {}

    clean = {}

    for key, value in parameters.items():

        if hasattr(value, "__iter__"):
            clean[key] = []
            for v in value:
                if hasattr(v, "string_value"):
                    clean[key].append(v.string_value)
            continue

        kind = value.WhichOneof("kind")

        if kind == "string_value":
            clean[key] = value.string_value
        elif kind == "number_value":
            clean[key] = value.number_value
        elif kind == "bool_value":
            clean[key] = value.bool_value
        else:
            clean[key] = None

    return clean

def normalize(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""

def clean_params(params):
    clean = {}
    for key, value in params.items():
        if hasattr(value, "__iter__") and not isinstance(value, str):
            clean[key] = list(value)
        else:
            clean[key] = value
    return clean


def detect_intent_cx(project_id, location, agent_id, text, language_code="en-us"):

    agent = f"projects/{project_id}/locations/{location}/agents/{agent_id}"
    session_path = f"{agent}/sessions/test_session"

    client = dialogflowcx.SessionsClient()

    response = client.detect_intent(
        request=dialogflowcx.DetectIntentRequest(
            session=session_path,
            query_input=dialogflowcx.QueryInput(
                text=dialogflowcx.TextInput(text=text),
                language_code=language_code
            )
        )
    )

    messages = []
    for msg in response.query_result.response_messages:
        if msg.text:
            messages.extend(msg.text.text)
    # raw_params = dict(response.query_result.parameters)
    # params = clean_params(raw_params)
    params = extract_cx_params(response.query_result.parameters)
    print("CX parameters:", params)

    order = {
    "pizza_type": normalize(params.get("pizza_type")),
    "pizza_size": normalize(params.get("pizza_size")),
    "pizza_toppings": ", ".join(params.get("pizza_toppings", [])),
    "name": normalize(params.get("customer_name")),
    "phone": normalize(params.get("phone_number"))}

    current_page = response.query_result.current_page.display_name
    print("Current page:", current_page)

    if current_page == "OrderPlaced":
        save_cx_order(order)
        print("CX order saved")

    return " ".join(messages)




# from google.cloud import dialogflowcx_v3beta1 as dialogflowcx

# def detect_intent_cx(project_id, location_id, agent_id, text, language_code="en-us"):

#     agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"

#     session_id = "test_session"
#     session_path = f"{agent}/sessions/{session_id}"
#     session_client = dialogflowcx.SessionsClient()

#     text_input = dialogflowcx.TextInput(text=text)
#     query_input = dialogflowcx.QueryInput(
#         text=text_input,
#         language_code=language_code
#     )

#     request = dialogflowcx.DetectIntentRequest(
#         session=session_path,
#         query_input=query_input
#     )

#     response = session_client.detect_intent(request=request)
#     print(response)

#     messages = []
#     for msg in response.query_result.response_messages:
#         if msg.text:
#             messages.extend(msg.text.text)

#     return " ".join(messages)
