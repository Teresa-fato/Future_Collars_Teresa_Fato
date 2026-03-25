"""
Weather Forecast (OOP) — Rain prediction using a WeatherForecast class.
Implements __setitem__, __getitem__, __iter__, and items().
Results are cached to a local JSON file; API calls only when needed.

Usage:
    python weather_forecast_oop.py
"""

import os
import json
import requests
from datetime import datetime, timedelta


# ── Configuration ─────────────────────────────────────────────────────

# Prague, Czech Republic (change to your preferred city)
LATITUDE = 50.0755
LONGITUDE = 14.4378
CITY_NAME = "Prague"

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={latitude}"
    "&longitude={longitude}"
    "&daily=precipitation_sum"
    "&timezone=Europe%2FLondon"
    "&start_date={searched_date}"
    "&end_date={searched_date}"
)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(DATA_DIR, "weather_cache.json")


# ── WeatherForecast Class ────────────────────────────────────────────


class WeatherForecast:
    """
    Weather forecast manager with dict-like access and file caching.

    Supports:
        forecast[date] = value     → __setitem__: store a forecast
        forecast[date]             → __getitem__: retrieve (from cache or API)
        for date in forecast:      → __iter__: iterate over known dates
        forecast.items()           → items: generator of (date, weather) tuples
    """

    def __init__(self, cache_file=CACHE_FILE):
        self._cache_file = cache_file
        self._data = self._load_cache()

    # ── File I/O ──────────────────────────────────────────────────────

    def _load_cache(self):
        """Load cached weather results from JSON file."""
        try:
            with open(self._cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {}
        except FileNotFoundError:
            return {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [!] Warning: Could not load cache ({e}). Starting fresh.")
            return {}

    def _save_cache(self):
        """Save cached weather results to JSON file."""
        try:
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError as e:
            print(f"  [!] Warning: Could not save cache ({e}).")

    # ── API Request ───────────────────────────────────────────────────

    def _fetch_from_api(self, date_str):
        """Fetch precipitation data from Open-Meteo API for a given date."""
        url = API_URL.format(
            latitude=LATITUDE,
            longitude=LONGITUDE,
            searched_date=date_str,
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            daily = data.get("daily", {})
            precipitation_list = daily.get("precipitation_sum", [])

            if precipitation_list and len(precipitation_list) > 0:
                return precipitation_list[0]
            else:
                return None

        except requests.exceptions.ConnectionError:
            print("  [!] Connection error. Check your internet connection.")
            return None
        except requests.exceptions.Timeout:
            print("  [!] Request timed out. Try again later.")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"  [!] HTTP error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  [!] Request error: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"  [!] Error parsing API response: {e}")
            return None

    # ── Interpretation ────────────────────────────────────────────────

    @staticmethod
    def interpret(value):
        """Interpret precipitation value into a human-readable message."""
        if value is None or value < 0:
            return "I don't know"
        elif value == 0.0:
            return "It will not rain"
        else:
            return f"It will rain (precipitation: {value} mm)"

    # ── Magic Methods ─────────────────────────────────────────────────

    def __setitem__(self, date_str, value):
        """Set a weather forecast for a particular date.

        Usage: forecast["2024-01-15"] = 2.3
        """
        self._data[date_str] = value
        self._save_cache()

    def __getitem__(self, date_str):
        """Get the weather forecast for a particular date.

        If the date is cached, return from cache.
        Otherwise, fetch from the API, cache it, and return.

        Usage: result = forecast["2024-01-15"]
        """
        if date_str in self._data:
            print(f"  [cached] Using saved result for {date_str}")
            return self._data[date_str]

        print(f"  [api] Fetching weather data for {date_str}...")
        value = self._fetch_from_api(date_str)
        self._data[date_str] = value
        self._save_cache()
        return value

    def __iter__(self):
        """Iterate over all dates for which the weather forecast is known.

        Usage: for date in forecast: print(date)
        """
        return iter(self._data)

    def items(self):
        """Generator of (date, weather) tuples for all saved results.

        Usage: for date, weather in forecast.items(): ...
        """
        for date_str, value in self._data.items():
            yield date_str, value

    def __len__(self):
        """Return the number of cached forecasts."""
        return len(self._data)

    def __contains__(self, date_str):
        """Check if a date has a cached forecast."""
        return date_str in self._data

    def __repr__(self):
        return f"WeatherForecast({len(self._data)} dates cached)"


# ── Date Input Helper ─────────────────────────────────────────────────


def get_date_from_user():
    """Prompt user for a date. Returns date string in YYYY-mm-dd format."""
    date_str = input("\n  Enter date to check (YYYY-mm-dd), or press Enter for tomorrow: ").strip()

    if not date_str:
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        print(f"  Using tomorrow's date: {date_str}")
        return date_str

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print(f"  [!] Invalid date format: '{date_str}'. Please use YYYY-mm-dd.")
        return None


# ── Main Loop ─────────────────────────────────────────────────────────


def main():
    """Main application loop demonstrating WeatherForecast class usage."""
    print("\n  ╔═══════════════════════════════════════════╗")
    print(f"  ║   Weather Forecast (OOP) — {CITY_NAME:<13}  ║")
    print("  ╚═══════════════════════════════════════════╝")
    print(f"  Coordinates: {LATITUDE}°N, {LONGITUDE}°E")

    forecast = WeatherForecast()
    print(f"  {forecast}")

    while True:
        print("\n  Commands: check, history, end")
        command = input("  Enter command: ").strip().lower()

        if command == "check":
            date_str = get_date_from_user()
            if date_str is None:
                continue

            # Use __getitem__ → forecast[date]
            value = forecast[date_str]
            print(f"  → {WeatherForecast.interpret(value)}")

        elif command == "history":
            if len(forecast) == 0:
                print("\n  No forecasts saved yet.")
            else:
                print(f"\n  Saved forecasts ({len(forecast)}):")
                print("  " + "-" * 50)

                # Use items() → generator of (date, weather) tuples
                for date, value in forecast.items():
                    print(f"  {date}  →  {WeatherForecast.interpret(value)}")

                print("  " + "-" * 50)

                # Use __iter__ → iterate over known dates
                print(f"\n  Known dates: {', '.join(d for d in forecast)}")

        elif command == "end":
            print("\n  Goodbye!\n")
            break

        else:
            print(f"  [!] Unknown command: '{command}'.")


if __name__ == "__main__":
    main()
