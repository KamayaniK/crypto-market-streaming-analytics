import os
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

api_key = os.getenv("COINGECKO_API_KEY")

# CoinGecko API endpoint
url = "https://api.coingecko.com/api/v3/simple/price"

# Cryptocurrencies we are tracking
params = {
    "ids": "bitcoin,ethereum,solana",
    "vs_currencies": "usd",
    "include_market_cap": "true",
    "include_24hr_vol": "true",
    "include_24hr_change": "true"
}

headers = {
    "x-cg-demo-api-key": api_key
}

response = requests.get(url, params=params, headers=headers, timeout=10)

print("HTTP Status:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("\nLIVE CRYPTO DATA")
    print("=" * 50)

    for coin, values in data.items():
        print(f"\n{coin.upper()}")
        print(f"Price: ${values.get('usd')}")
        print(f"Market Cap: ${values.get('usd_market_cap')}")
        print(f"24h Volume: ${values.get('usd_24h_vol')}")
        print(f"24h Change: {values.get('usd_24h_change')}%")

    print("\n" + "=" * 50)
    print("SUCCESS: Live data received from CoinGecko!")

else:
    print("API request failed.")
    print(response.text)