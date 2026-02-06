from google.cloud import dialogflowcx_v3beta1 as dialogflowcx
from db_cx import save_cx_order
# import uuid   
# CURRENT_SESSION_ID = str(uuid.uuid4()) 

CX_CLIENT = dialogflowcx.SessionsClient()

# def reset_session():
#     global CURRENT_SESSION_ID
#     CURRENT_SESSION_ID = str(uuid.uuid4())
#     print("CX session reset:", CURRENT_SESSION_ID)

def extract_cx_params(parameters):
    clean = {}

    if not parameters:
        return clean

    for key, value in parameters.items():

        if isinstance(value, (str, int, float, bool)):
            clean[key] = value
            continue

        if hasattr(value, "WhichOneof"):
            kind = value.WhichOneof("kind")

            if kind == "string_value":
                clean[key] = value.string_value
            elif kind == "number_value":
                clean[key] = value.number_value
            elif kind == "bool_value":
                clean[key] = value.bool_value
            elif kind == "list_value":
                clean[key] = [
                    v.string_value
                    for v in value.list_value.values
                    if v.string_value
                ]
            else:
                clean[key] = None
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


def detect_intent_cx_kfc(project_id, location, agent_id, text, session_id, language_code="en-us"):
    # global CURRENT_SESSION_ID

    agent = f"projects/{project_id}/locations/{location}/agents/{agent_id}"
    session_path = f"{agent}/sessions/{session_id}"

    # client = dialogflowcx.SessionsClient()

    response = CX_CLIENT.detect_intent(
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
    
    reply_text = " ".join(messages)
    params = extract_cx_params(response.query_result.parameters)
    print("KFC Parameters:", params)

    order = {
    "name": normalize(params.get("customer_name")),
    "phone": normalize(params.get("customer_number")),
    "address": normalize(params.get("customer_address")),
    "chicken_item": normalize(params.get("chicken_item")),
    "burger_item": normalize(params.get("burger_item")),
    "wrap_item": normalize(params.get("wrap_item")),
    "wings_item": normalize(params.get("wings_item")),
    "combo_item": normalize(params.get("combo_item")),
    "extras_item": normalize(params.get("extras_item")),
    "beverages_item": normalize(params.get("beverages_item")),
    }

    page = response.query_result.current_page.display_name
    flow = response.query_result.current_flow.display_name

    print("CX Flow:", flow)
    print("CX Page:", page)
    print("CX Session:", CURRENT_SESSION_ID)

    if flow == "Default Start Flow":
        save_cx_order(order)
        print("KFC order saved")
        reset_session()

    return {
        "reply": reply_text,
        "flow": flow,
        "page": page,
        "params": params
    }
