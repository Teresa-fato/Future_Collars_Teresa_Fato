"""
Weather Checker — Check if it's going to rain on a given date.
Uses the Open-Meteo API for precipitation forecasts.
Results are cached to a local file to avoid redundant API calls.

Usage:
    python weather_checker.py
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


# ── Cache I/O ─────────────────────────────────────────────────────────


def load_cache():
    """Load cached weather results from file."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [!] Warning: Could not load cache ({e}). Starting fresh.")
        return {}


def save_cache(cache):
    """Save cached weather results to file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except OSError as e:
        print(f"  [!] Warning: Could not save cache ({e}).")


# ── Date Handling ─────────────────────────────────────────────────────


def get_date_from_user():
    """Prompt user for a date. Returns date string in YYYY-mm-dd format."""
    date_str = input("\n  Enter date to check (YYYY-mm-dd), or press Enter for tomorrow: ").strip()

    if not date_str:
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        print(f"  Using tomorrow's date: {date_str}")
        return date_str

    # Validate format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print(f"  [!] Invalid date format: '{date_str}'. Please use YYYY-mm-dd.")
        return None


# ── API Request ───────────────────────────────────────────────────────


def fetch_precipitation(date_str):
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


# ── Result Interpretation ─────────────────────────────────────────────


def interpret_precipitation(value):
    """Interpret precipitation value and return a human-readable message."""
    if value is None or value < 0:
        return "I don't know"
    elif value == 0.0:
        return "It will not rain"
    else:
        return f"It will rain (precipitation: {value} mm)"


# ── Main Loop ─────────────────────────────────────────────────────────


def main():
    """Main application loop."""
    print("\n  ╔═══════════════════════════════════════╗")
    print(f"  ║   Weather Checker — {CITY_NAME:<17} ║")
    print("  ╚═══════════════════════════════════════╝")
    print(f"  Coordinates: {LATITUDE}°N, {LONGITUDE}°E")

    cache = load_cache()

    while True:
        date_str = get_date_from_user()
        if date_str is None:
            continue

        # Check cache first
        if date_str in cache:
            print(f"\n  [cached] Result for {date_str}:")
            value = cache[date_str]
            print(f"  → {interpret_precipitation(value)}")
        else:
            # Fetch from API
            print(f"\n  Fetching weather data for {date_str}...")
            value = fetch_precipitation(date_str)

            # Cache the result (even None, to avoid repeated failed lookups)
            cache[date_str] = value
            save_cache(cache)

            print(f"  → {interpret_precipitation(value)}")

        # Ask to continue
        again = input("\n  Check another date? (y/n): ").strip().lower()
        if again != "y":
            print("\n  Goodbye!\n")
            break


if __name__ == "__main__":
    main()
