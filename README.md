# weather-cli

A command-line tool for checking weather using the OpenWeatherMap API.

## Features

- Current weather conditions
- 5-day weather forecast
- Support for metric and imperial units
- Clean, formatted output

## Installation

```bash
# Clone the repository
git clone https://github.com/souvikghosh/weather-cli.git
cd weather-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Setup

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Set the environment variable:

```bash
export OPENWEATHER_API_KEY="your_api_key_here"
```

## Usage

```bash
# Get current weather
weather London
weather "New York"
weather Tokyo --units imperial

# Get 5-day forecast
weather London --forecast
weather Paris -f -u metric
```

## Example Output

```
$ weather London
Weather for London, GB
────────────────────────────────────────
Temperature:  15.2°C (feels like 14.8°C)
Conditions:   Partly cloudy
Humidity:     72%
Wind:         3.5 m/s
────────────────────────────────────────
Updated: 2026-01-28 14:30

$ weather London --forecast
5-Day Forecast for London
──────────────────────────────────────────────────
Mon Jan 28   12.0°C -  16.5°C  Partly cloudy
Tue Jan 29   10.5°C -  14.2°C  Light rain
Wed Jan 30    9.0°C -  13.8°C  Cloudy
Thu Jan 31   11.2°C -  15.0°C  Clear sky
Fri Feb 01   13.0°C -  17.5°C  Sunny
```

## Options

| Option | Description |
|--------|-------------|
| `--forecast`, `-f` | Show 5-day forecast |
| `--units`, `-u` | Temperature units: `metric` (default) or `imperial` |

## License

MIT
