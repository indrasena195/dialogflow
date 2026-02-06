from flask import Flask, request, jsonify
from flask_cors import CORS
from es_handler import detect_intent_es
from cx_handler import detect_intent_cx
from cx_kfc import detect_intent_cx_kfc
import os

print(" Flask loaded THIS server.py file")  # DEBUG

app = Flask(__name__)

# Enable full CORS for all domains
CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/chat", methods=["OPTIONS"])
def chat_options():
    print("OPTIONS preflight request received")  # DEBUG
    return jsonify({"status": "ok"}), 200

AGENTS = {
    "agent1": {
        "type": "es",
        "project_id": "booking-npbk"
    },
    "agent2": {
        "type": "cx-flow",
        "project_id": "dialogflow-test-475718",
        "location": "global",
        "agent_id": "8a7b131d-3823-4f4b-b5f1-25a4868fda9f"
    },
    "agent3": {
        "type": "cx-playbook",
        "project_id": "dialogflow-test-475718",
        "location": "global",
        "agent_id": "db914a76-18ab-4e79-aea5-bbbfb9c659a5"
    },
    "agent4": {
        "type": "cx-kfc",
        "project_id": "dialogflow-test-475718",
        "location": "global",
        "agent_id": "8574aa62-0d97-47fa-b483-c3537d6e1e24"
    }
}

@app.route("/chat", methods=["POST"])
def chat():
    print("POST /chat reached")   # DEBUG
    data = request.get_json()
    print("Received payload:", data)

    agent_selected = data["agent"]
    text = data["message"]

    config = AGENTS.get(agent_selected)

    if not config:
        return jsonify({"reply": "Invalid agent"})

    if config["type"] == "es":
        reply = detect_intent_es(config["project_id"], text)
    elif config["type"] == "cx-flow":
        reply = detect_intent_cx(
            config["project_id"],
            config["location"],
            config["agent_id"],
            text
        )
    elif config["type"] == "cx-playbook":
        reply = detect_intent_cx(
            config["project_id"],
            config["location"],
            config["agent_id"],
            text
        )
    elif config["type"] == "cx-kfc":
        reply = detect_intent_cx_kfc(
            config["project_id"],
            config["location"],
            config["agent_id"],
            text
        )
    else:
        reply = "Unknown agent type"

    print("Dialogflow response:", reply)
    return jsonify({"response": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

# if __name__ == "__main__":
#     app.run(port=5001, debug=False)
