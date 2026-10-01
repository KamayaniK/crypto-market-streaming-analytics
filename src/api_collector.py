import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("COINGECKO_API_KEY")

if not API_KEY:
    raise ValueError("COINGECKO_API_KEY not found in .env file")


# --------------------------------------------------
# CoinGecko configuration
# --------------------------------------------------

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

COINS = [
    "bitcoin",
    "ethereum",
    "solana",
    "ripple",
    "dogecoin"
]

COLLECTION_INTERVAL = 300  # 5 minutes


# --------------------------------------------------
# Fetch live market data
# --------------------------------------------------

def fetch_market_data():

    params = {
        "vs_currency": "usd",
        "ids": ",".join(COINS),
        "order": "market_cap_desc",
        "per_page": 5,
        "page": 1,
        "sparkline": "false"
    }

    headers = {
        "x-cg-demo-api-key": API_KEY
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# Convert API response into streaming events
# --------------------------------------------------

def create_events(market_data):

    timestamp = datetime.now(timezone.utc).isoformat()

    events = []

    for coin in market_data:

        event = {
            "timestamp": timestamp,
            "coin_id": coin["id"],
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "price_usd": coin["current_price"],
            "market_cap_usd": coin["market_cap"],
            "volume_24h_usd": coin["total_volume"],
            "price_change_24h_pct": coin["price_change_percentage_24h"],
            "market_cap_rank": coin["market_cap_rank"]
        }

        events.append(event)

    return events


# --------------------------------------------------
# Display events
# --------------------------------------------------

def display_events(events):

    print("\n" + "=" * 80)
    print("LIVE CRYPTO MARKET SNAPSHOT")
    print("=" * 80)

    for event in events:

        print(
            f"{event['symbol']:>6} | "
            f"Price: ${event['price_usd']:,.2f} | "
            f"24h Change: {event['price_change_24h_pct']:.2f}% | "
            f"Volume: ${event['volume_24h_usd']:,.0f}"
        )

    print("=" * 80)
    print(f"Timestamp: {events[0]['timestamp']}")
    print("=" * 80)


# --------------------------------------------------
# Main streaming collector
# --------------------------------------------------

def main():

    print("Crypto Market Collector Started")
    print("Tracking:", ", ".join(COINS))
    print("Collection interval: 5 minutes")
    print("Press CTRL+C to stop.\n")

    while True:

        try:

            market_data = fetch_market_data()

            events = create_events(market_data)

            display_events(events)

        except requests.exceptions.RequestException as error:

            print("\nAPI request failed:")
            print(error)

        except Exception as error:

            print("\nUnexpected error:")
            print(error)

        time.sleep(COLLECTION_INTERVAL)


if __name__ == "__main__":
    main()