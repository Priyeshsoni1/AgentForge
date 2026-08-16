from datetime import datetime
from zoneinfo import ZoneInfo


def get_time(city: str) -> str:
    timezones = {
        "delhi": "Asia/Kolkata",
        "london": "Europe/London",
        "new york": "America/New_York",
        "tokyo": "Asia/Tokyo",
    }

    timezone = timezones.get(city.lower())

    if not timezone:
        return f"Timezone not supported for {city}"

    current_time = datetime.now(ZoneInfo(timezone))

    return current_time.strftime("%Y-%m-%d %H:%M:%S")