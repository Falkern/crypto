import requests
from difflib import get_close_matches
import json
import os
import time

COIN_LIST_FILE = "coin_list.json"

def load_coin_list():
    if os.path.exists(COIN_LIST_FILE):
        with open(COIN_LIST_FILE, "r") as f:
            print("Loading coin list from cache...")
            return json.load(f)
    
    print("Fetching the latest coin list from CoinGecko...")
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        coin_list = response.json()

        with open(COIN_LIST_FILE, "w") as f:
            json.dump(coin_list, f)
        return coin_list
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the coin list: {e}")
        retry = input("Would you like to retry? (y/n): ").strip().lower()
        if retry == 'y':
            return load_coin_list()
        else:
            return []

def find_coin_id(coin_name, coin_list):
    coin_names = [coin['name'].lower() for coin in coin_list]
    matches = get_close_matches(coin_name.lower(), coin_names, n=1, cutoff=0.6)
    if matches:
        matched_name = matches[0]
        matched_coin = next((coin for coin in coin_list if coin['name'].lower() == matched_name), None)
        return matched_coin['id'] if matched_coin else None
    return None

def get_crypto_price(crypto_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get(crypto_id, {}).get('usd', 'Price not available')
    except requests.exceptions.RequestException as e:
        return f"Failed to retrieve price: {e}"

def main():
    print("\nWelcome to the Crypto Price Tracker CLI!")
    print("Type the names of the cryptocurrencies you want prices for, separated by commas.")

    coin_list = load_coin_list()
    if not coin_list:
        return

    coin_input = input("Enter the names of the cryptocurrencies: ")
    coin_names = [coin.strip() for coin in coin_input.split(",")]
    coin_prices = {}

    print("\nFetching prices...")
    time.sleep(1)

    for coin_name in coin_names:
        coin_id = find_coin_id(coin_name, coin_list)
        if coin_id:
            price = get_crypto_price(coin_id)
            if isinstance(price, float):
                coin_prices[coin_name] = f"{price:.2f}"
            else:
                coin_prices[coin_name] = price
        else:
            coin_prices[coin_name] = "Coin not found"

    print("\nHere are the prices of the cryptocurrencies you requested:")
    print("-" * 40)
    for coin_name, price in coin_prices.items():
        print(f"{coin_name.title()}: ${price}")
    print("-" * 40)
    print("Prices are fetched from CoinGecko.\n")

if __name__ == "__main__":
    main()
