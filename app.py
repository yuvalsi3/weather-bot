from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Dialogflow webhook is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName")
    parameters = req.get("queryResult", {}).get("parameters", {})
    city = parameters.get("city", "your city")

    if intent == "GetWeather":
        response_text = f"The weather in {city} is sunny with 25°C ☀️"
    else:
        response_text = "Sorry, I can't handle that yet."

    return jsonify({"fulfillmentText": response_text})
