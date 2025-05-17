from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()

    # Get intent name
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName")

    # Get city parameter
    parameters = req.get("queryResult", {}).get("parameters", {})
    city = parameters.get("city", "your city")

    if intent == "GetWeather":
        response_text = f"The weather in {city} is sunny with 25°C ☀️"
    else:
        response_text = "Sorry, I don't know how to handle that yet."

    return jsonify({"fulfillmentText": response_text})


if __name__ == '__main__':
    app.run(port=5000)
