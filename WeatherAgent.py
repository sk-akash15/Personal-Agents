import google.generativeai as genai
import requests

# === CONFIG ===
genai.configure(api_key="AIzaSyA4hVbpZeQL0-VoqUj6tPlj92py8lCS7II")  

# === Helper: Geocode city to lat/lon ===
def get_coordinates(city: str):
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    res = requests.get(geocode_url)
    if res.status_code == 200 and res.json().get("results"):
        data = res.json()["results"][0]
        return data["latitude"], data["longitude"]
    else:
        return None, None

# === Weather tool function ===
def get_weather(location: str) -> str:
    """Returns the current weather for the given location using Open-Meteo API."""
    lat, lon = get_coordinates(location)
    if lat is None or lon is None:
        return f"Sorry, I couldn't find the coordinates for '{location}'."

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true"
    )
    res = requests.get(url)
    if res.status_code == 200:
        weather = res.json().get("current_weather", {})
        temp = weather.get("temperature")
        wind = weather.get("windspeed")
        cond = weather.get("weathercode", "unknown condition")
        return (
            f"The current temperature in {location} is {temp}°C with wind speed of {wind} km/h."
        )
    else:
        return f"Sorry, I couldn’t fetch the weather for '{location}'."

# === Gemini LLM with bound tool ===
model = genai.GenerativeModel("gemini-1.5-pro")
weather_agent = model.bind_tools([get_weather])

# === User interaction ===
print("🌤️ Weather Agent ready! Ask me about the weather. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    response = weather_agent.generate_content(user_input)
    print("🤖 Gemini:", response.text)
