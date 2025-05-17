from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get API key from environment variable or hardcoded string
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or "0ced9c6e5e56f78ae723835201973cd2"

@app.route('/')
def index():
    return "Dialogflow webhook with real weather is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName")
    parameters = req.get("queryResult", {}).get("parameters", {})
    city = parameters.get("city")

    if intent == "GetWeather" and city:
        weather = get_weather_for_city(city)
        response_text = weather or f"Sorry, I couldn’t get the weather for {city}."
    else:
        response_text = "Sorry, I didn't understand that."

    return jsonify({"fulfillmentText": response_text})

def get_weather_for_city(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return None

        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        return f"The weather in {city} is {description}, {temp}°C."
    except Exception as e:
        return None
