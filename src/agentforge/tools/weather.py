def get_weather(city: str) -> str:
    weather_data = {
        "delhi": "32°C, Sunny",
        "mumbai": "29°C, Cloudy",
        "london": "18°C, Rainy",
        "tokyo": "26°C, Clear",
    }

    return weather_data.get(
        city.lower(),
        f"Weather data unavailable for {city}"
    )