# webhook_bot.py
# גרסה ל-Dialogflow עם Flask + Webhook + OpenWeatherMap

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WEATHER_API_KEY = "0ced9c6e5e56f78ae723835201973cd2"

# ניקוי שם עיר

def normalize_city_name(city):
    corrections = {
        "תל אביב": "Tel Aviv",
        "תל-אביב": "Tel Aviv",
        "ירושליים": "Jerusalem",
        "ירושלים": "Jerusalem",
        "ראשון לציון": "Rishon LeZion",
        "בת ים": "Bat Yam",
        "חיפה": "Haifa",
        "אשדוד": "Ashdod",
        "נתניה": "Netanya",
        "באר שבע": "Beersheba",
        "צפת": "Safed"
    }
    return corrections.get(city.strip(), city)

# שליפת תחזית

def get_weather(city):
    city_eng = normalize_city_name(city)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_eng}&appid={WEATHER_API_KEY}&units=metric&lang=he"
    response = requests.get(url)
    data = response.json()

    if "main" not in data or "weather" not in data:
        message = data.get("message", "שגיאה לא ידועה")
        raise ValueError(f"שגיאה בשליפת מזג האוויר לעיר {city}: {message}")

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    return temp, description

# המלצת לבוש לפי פעילות ושעה

def get_activity_based_clothes(activity, temp, time_of_day):
    activity = activity.lower()
    time_of_day = time_of_day.lower()

    ערב = ["ערב", "לילה"]
    is_evening = any(t in time_of_day for t in ערב)

    if "ריצה" in activity:
        return "👕 חולצה נושמת, 🩳 מכנס ספורט, 👟 נעלי ריצה"
    elif "טיול" in activity or "הליכה" in activity:
        if temp < 18 or is_evening:
            return "🧥 שכבה חמה, 👟 נעליים סגורות, 👖 מכנסיים ארוכים"
        else:
            return "👕 חולצה קצרה, 🧢 כובע, 👟 נעליים סגורות"
    else:
        if temp < 12:
            return "🧥 מעיל, 👖 מכנסיים ארוכים, 🧣 צעיף"
        elif temp < 20:
            return "🧥 סווטשירט קל, 👕 חולצה ארוכה"
        else:
            return "👕 חולצה קצרה, 🩳 מכנסיים קצרים"

# Webhook ל-Dialogflow

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    parameters = req.get("queryResult", {}).get("parameters", {})

    city = parameters.get("geo-city", "תל אביב")
    activity = parameters.get("activity", "")
    time_of_day = parameters.get("time", "")

    try:
        temp, desc = get_weather(city)
        clothes = get_activity_based_clothes(activity, temp, time_of_day)
        response_text = f"ב{city} כעת {temp}° עם {desc}. מומלץ ללבוש: {clothes}"
    except Exception as e:
        response_text = f"מצטערת, לא הצלחתי להביא את התחזית: {e}"

    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
