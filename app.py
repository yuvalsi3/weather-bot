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

        # 🧥 Clothing recommendation logic
        if temp < 10:
            clothing = "It's quite cold — wear a warm coat and scarf 🧥🧣"
        elif temp < 18:
            clothing = "You might want to wear a jacket 🧥"
        elif temp < 25:
            clothing = "A t-shirt and jeans should be fine 👕👖"
        else:
            clothing = "It's hot! Wear something light 🩳👒"

        return f"The weather in {city} is {description}, {temp}°C. {clothing}"
    except Exception:
        return None


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
