#!/usr/bin/env python3
"""
weather-cli: Get current weather and forecasts from the command line.

Usage:
    weather <city>              Get current weather
    weather <city> --forecast   Get 5-day forecast

Requires OPENWEATHER_API_KEY environment variable.
"""

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime

import requests

API_BASE = "https://api.openweathermap.org/data/2.5"


@dataclass
class Weather:
    city: str
    country: str
    temp: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    timestamp: datetime


@dataclass
class Forecast:
    date: datetime
    temp_min: float
    temp_max: float
    description: str


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("OPENWEATHER_API_KEY")
    if not key:
        print("Error: OPENWEATHER_API_KEY environment variable not set", file=sys.stderr)
        print("Get a free API key at: https://openweathermap.org/api", file=sys.stderr)
        sys.exit(1)
    return key


def fetch_current_weather(city: str, api_key: str, units: str = "metric") -> Weather:
    """Fetch current weather for a city."""
    url = f"{API_BASE}/weather"
    params = {"q": city, "appid": api_key, "units": units}

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 404:
        print(f"Error: City '{city}' not found", file=sys.stderr)
        sys.exit(1)
    elif response.status_code == 401:
        print("Error: Invalid API key", file=sys.stderr)
        sys.exit(1)

    response.raise_for_status()
    data = response.json()

    return Weather(
        city=data["name"],
        country=data["sys"]["country"],
        temp=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        humidity=data["main"]["humidity"],
        description=data["weather"][0]["description"],
        wind_speed=data["wind"]["speed"],
        timestamp=datetime.fromtimestamp(data["dt"]),
    )


def fetch_forecast(city: str, api_key: str, units: str = "metric") -> list[Forecast]:
    """Fetch 5-day forecast for a city."""
    url = f"{API_BASE}/forecast"
    params = {"q": city, "appid": api_key, "units": units}

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 404:
        print(f"Error: City '{city}' not found", file=sys.stderr)
        sys.exit(1)
    elif response.status_code == 401:
        print("Error: Invalid API key", file=sys.stderr)
        sys.exit(1)

    response.raise_for_status()
    data = response.json()

    # Group by day and get min/max temps
    daily: dict[str, dict] = {}
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        day_key = dt.strftime("%Y-%m-%d")

        if day_key not in daily:
            daily[day_key] = {
                "date": dt,
                "temps": [],
                "descriptions": [],
            }

        daily[day_key]["temps"].append(item["main"]["temp"])
        daily[day_key]["descriptions"].append(item["weather"][0]["description"])

    forecasts = []
    for day_data in daily.values():
        # Get most common description
        desc = max(set(day_data["descriptions"]), key=day_data["descriptions"].count)
        forecasts.append(
            Forecast(
                date=day_data["date"],
                temp_min=min(day_data["temps"]),
                temp_max=max(day_data["temps"]),
                description=desc,
            )
        )

    return forecasts[:5]


def format_weather(weather: Weather, units: str) -> str:
    """Format weather for display."""
    temp_unit = "°C" if units == "metric" else "°F"
    speed_unit = "m/s" if units == "metric" else "mph"

    lines = [
        f"Weather for {weather.city}, {weather.country}",
        f"{'─' * 40}",
        f"Temperature:  {weather.temp:.1f}{temp_unit} (feels like {weather.feels_like:.1f}{temp_unit})",
        f"Conditions:   {weather.description.capitalize()}",
        f"Humidity:     {weather.humidity}%",
        f"Wind:         {weather.wind_speed:.1f} {speed_unit}",
        f"{'─' * 40}",
        f"Updated: {weather.timestamp.strftime('%Y-%m-%d %H:%M')}",
    ]
    return "\n".join(lines)


def format_forecast(forecasts: list[Forecast], city: str, units: str) -> str:
    """Format forecast for display."""
    temp_unit = "°C" if units == "metric" else "°F"

    lines = [f"5-Day Forecast for {city}", f"{'─' * 50}"]

    for fc in forecasts:
        day = fc.date.strftime("%a %b %d")
        lines.append(
            f"{day}  {fc.temp_min:5.1f}{temp_unit} - {fc.temp_max:5.1f}{temp_unit}  {fc.description.capitalize()}"
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="weather",
        description="Get weather information from the command line",
    )
    parser.add_argument("city", nargs="+", help="City name (e.g., 'London' or 'New York')")
    parser.add_argument(
        "--forecast", "-f", action="store_true", help="Show 5-day forecast"
    )
    parser.add_argument(
        "--units",
        "-u",
        choices=["metric", "imperial"],
        default="metric",
        help="Temperature units (default: metric)",
    )

    args = parser.parse_args()
    city = " ".join(args.city)
    api_key = get_api_key()

    if args.forecast:
        forecasts = fetch_forecast(city, api_key, args.units)
        print(format_forecast(forecasts, city, args.units))
    else:
        weather = fetch_current_weather(city, api_key, args.units)
        print(format_weather(weather, args.units))


if __name__ == "__main__":
    main()
