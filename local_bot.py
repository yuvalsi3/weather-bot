# local_bot.py
# גרסה מקומית של הצ'אטבוט בעברית מלאה, עם חיבור ל-OpenWeatherMap

import requests

# 🔑 הכניסי כאן את המפתח שלך מ-OpenWeatherMap
WEATHER_API_KEY = '0ced9c6e5e56f78ae723835201973cd2'


# פונקציה לניקוי שם עיר נפוץ עם שגיאות

def normalize_city_name(city):
    corrections = {
        "תל אביב": "Tel Aviv",
        "תל-אביב": "Tel Aviv",
        "ירושליים": "Jerusalem",
        "ראשון לציון": "Rishon LeZion",
        "בת ים": "Bat Yam",
        "חיפה": "Haifa",
        "אשדוד": "Ashdod",
        "נתניה": "Netanya",
        "באר שבע": "Beersheba",
        "צפת": "Safed"
    }
    return corrections.get(city.strip(), city)

# פונקציה לשליפת תחזית

def get_weather(city):
    city_eng = normalize_city_name(city)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_eng}&appid={WEATHER_API_KEY}&units=metric&lang=he"
    response = requests.get(url)
    data = response.json()

    # בדיקה אם התקבלה תשובה תקינה
    if "main" not in data or "weather" not in data:
        message = data.get("message", "שגיאה לא ידועה")
        raise ValueError(f"שגיאה בשליפת מזג האוויר לעיר {city}: {message}")

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    return temp, description

# פונקציה לזיהוי המלצה לפי פעילות ושעה ביום

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

# צ'אט טקסטואלי פשוט מול המשתמש

def main():
    print("👋 ברוכה הבאה לצ'אטבוט המלצות לבוש לפי מזג האוויר!")
    city = input("📍 באיזו עיר תהיי? ")
    activity = input("🏃‍♀️ מה את מתכננת לעשות? (למשל: ריצה, טיול, להסתובב...) ")
    time_of_day = input("🕒 באיזו שעה? (בוקר / צהריים / ערב / לילה): ")

    try:
        temp, desc = get_weather(city)
        clothes = get_activity_based_clothes(activity, temp, time_of_day)
        print(f"\nב{city} כעת {temp}° עם {desc}. מומלץ ללבוש: {clothes}\n")
    except ValueError as e:
        print(f"❌ שגיאה: {e}")

if __name__ == '__main__':
    main()
