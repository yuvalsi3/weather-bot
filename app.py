from datetime import datetime

from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    elif intent == "GetTripAdvice":
        city = parameters.get("city")
        date_period = parameters.get("date")
        start_date = date_period.get("startDate")
        end_date = date_period.get("endDate")
        formatted_start_date = format_iso_to_ddmmyyyy(start_date)
        formatted_end_date = format_iso_to_ddmmyyyy(end_date)
        forecast = get_forecast_for_date_range(city=city, start_date=start_date, end_date=end_date)
        response_text = f"You're visiting {city} between {formatted_start_date} to {formatted_end_date}. {forecast}"
    else:
        response_text = "Sorry, I didn't understand that."

    return jsonify({"fulfillmentText": response_text})

def format_iso_to_ddmmyyyy(iso_string):
    dt = datetime.fromisoformat(iso_string)
    return dt.strftime('%d/%m/%Y')

import requests
from datetime import datetime

def summarize_temperature_trend(forecast_list, city, start_date, end_date):
    if not forecast_list:
        return f"Sorry, no forecast data available for {city} between {start_date} and {end_date}."

    temps = [entry['temp'] for entry in forecast_list]
    descriptions = [entry['description'] for entry in forecast_list]

    avg_temp = sum(temps) / len(temps)
    min_temp = min(temps)
    max_temp = max(temps)

    # Determine trend (simple version)
    trend = "stable"
    if temps[-1] > temps[0] + 2:
        trend = "warming"
    elif temps[-1] < temps[0] - 2:
        trend = "cooling"

    # Most common description
    from collections import Counter
    common_desc = Counter(descriptions).most_common(1)[0][0]

    # Clothing advice
    if avg_temp < 10:
        clothes = "Pack warm clothes, including a coat and scarf 🧣🧥"
    elif avg_temp < 18:
        clothes = "You might want to take a jacket 🧥"
    elif avg_temp < 25:
        clothes = "T-shirts and jeans should be fine 👕👖"
    else:
        clothes = "It's hot — pack light clothes and stay hydrated 🩳👒"

    return (
        f"Here's the forecast for {city} from {start_date} to {end_date}:\n"
        f"- Average temperature: {avg_temp:.1f}°C\n"
        f"- Min: {min_temp:.1f}°C, Max: {max_temp:.1f}°C\n"
        f"- Most common condition: {common_desc}\n"
        f"- Temperature trend: {trend}\n"
        f"{clothes}"
    )


def get_forecast_for_date_range(city, start_date, end_date):
    url = f"http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        for entry in data.get("list", []):
            timestamp = entry["dt_txt"]
            date_str = timestamp.split(" ")[0]

            if start_date <= date_str <= end_date:
                forecasts.append({
                    "datetime": timestamp,
                    "temp": entry["main"]["temp"],
                    "description": entry["weather"][0]["description"].capitalize()
                })
        return summarize_temperature_trend(forecast_list=forecasts, city=city, start_date=start_date, end_date=end_date)
    except Exception as e:
        print("Error fetching forecast:", e)
        return []

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
    except Exception as e:
        print(str(e))
        return None


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
