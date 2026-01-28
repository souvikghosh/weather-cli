"""Tests for weather-cli."""

from datetime import datetime
from unittest.mock import patch

import pytest
import responses

from src.weather import (
    Weather,
    Forecast,
    fetch_current_weather,
    fetch_forecast,
    format_weather,
    format_forecast,
    get_api_key,
)

SAMPLE_WEATHER_RESPONSE = {
    "name": "London",
    "sys": {"country": "GB"},
    "main": {"temp": 15.2, "feels_like": 14.8, "humidity": 72},
    "weather": [{"description": "partly cloudy"}],
    "wind": {"speed": 3.5},
    "dt": 1706450400,
}

SAMPLE_FORECAST_RESPONSE = {
    "list": [
        {
            "dt": 1706450400,
            "main": {"temp": 12.0},
            "weather": [{"description": "cloudy"}],
        },
        {
            "dt": 1706461200,
            "main": {"temp": 14.0},
            "weather": [{"description": "cloudy"}],
        },
        {
            "dt": 1706536800,
            "main": {"temp": 10.0},
            "weather": [{"description": "rain"}],
        },
    ]
}


class TestGetApiKey:
    def test_returns_key_when_set(self, monkeypatch):
        monkeypatch.setenv("OPENWEATHER_API_KEY", "test_key")
        assert get_api_key() == "test_key"

    def test_exits_when_not_set(self, monkeypatch):
        monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
        with pytest.raises(SystemExit):
            get_api_key()


class TestFetchCurrentWeather:
    @responses.activate
    def test_fetch_success(self):
        responses.add(
            responses.GET,
            "https://api.openweathermap.org/data/2.5/weather",
            json=SAMPLE_WEATHER_RESPONSE,
            status=200,
        )
        weather = fetch_current_weather("London", "test_key")
        assert weather.city == "London"
        assert weather.country == "GB"
        assert weather.temp == 15.2
        assert weather.humidity == 72

    @responses.activate
    def test_fetch_city_not_found(self):
        responses.add(
            responses.GET,
            "https://api.openweathermap.org/data/2.5/weather",
            json={"message": "city not found"},
            status=404,
        )
        with pytest.raises(SystemExit):
            fetch_current_weather("InvalidCity", "test_key")

    @responses.activate
    def test_fetch_invalid_api_key(self):
        responses.add(
            responses.GET,
            "https://api.openweathermap.org/data/2.5/weather",
            json={"message": "Invalid API key"},
            status=401,
        )
        with pytest.raises(SystemExit):
            fetch_current_weather("London", "bad_key")


class TestFetchForecast:
    @responses.activate
    def test_fetch_forecast_success(self):
        responses.add(
            responses.GET,
            "https://api.openweathermap.org/data/2.5/forecast",
            json=SAMPLE_FORECAST_RESPONSE,
            status=200,
        )
        forecasts = fetch_forecast("London", "test_key")
        assert len(forecasts) >= 1
        assert isinstance(forecasts[0], Forecast)


class TestFormatWeather:
    def test_format_metric(self):
        weather = Weather(
            city="London",
            country="GB",
            temp=15.2,
            feels_like=14.8,
            humidity=72,
            description="partly cloudy",
            wind_speed=3.5,
            timestamp=datetime(2026, 1, 28, 14, 30),
        )
        output = format_weather(weather, "metric")
        assert "London, GB" in output
        assert "15.2°C" in output
        assert "72%" in output
        assert "m/s" in output

    def test_format_imperial(self):
        weather = Weather(
            city="London",
            country="GB",
            temp=59.4,
            feels_like=58.6,
            humidity=72,
            description="partly cloudy",
            wind_speed=7.8,
            timestamp=datetime(2026, 1, 28, 14, 30),
        )
        output = format_weather(weather, "imperial")
        assert "°F" in output
        assert "mph" in output


class TestFormatForecast:
    def test_format_forecast(self):
        forecasts = [
            Forecast(
                date=datetime(2026, 1, 28),
                temp_min=12.0,
                temp_max=16.5,
                description="partly cloudy",
            )
        ]
        output = format_forecast(forecasts, "London", "metric")
        assert "London" in output
        assert "12.0°C" in output
        assert "16.5°C" in output
