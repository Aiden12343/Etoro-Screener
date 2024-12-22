import sys
import json
import csv
import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- Load Instrument Map ---
def load_instrument_map():
    try:
        with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
            instrument_map = json.load(f)
    except FileNotFoundError:
        instrument_map = {}
    return instrument_map

# --- Add JSON Data to Portfolio CSV ---
def add_json_to_csv(json_data, csv_file_path, instrument_map):
    try:
        with open(csv_file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for username, portfolio_data in json_data.items():
                for position in portfolio_data:
                    instrument_id = position.get("InstrumentID", "N/A")
                    ticker_name = instrument_map.get(str(instrument_id), "Unknown Ticker")
                    writer.writerow([instrument_id, ticker_name, position.get("Direction", "N/A"),
                                     position.get("Invested", "N/A"), position.get("NetProfit", "N/A"),
                                     position.get("Value", "N/A"), username])
        print("Successfully updated CSV data.")
    except Exception as e:
        print(f"Error adding/updating CSV: {e}")

# --- Load CID Mapping ---
def load_cid_mapping(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    return {}

# --- Save CID Mapping ---
def save_cid_mapping(filepath, cid_mapping):
    with open(filepath, 'w') as file:
        json.dump(cid_mapping, file, indent=4)

# --- Append to CSV ---
def append_to_csv(filepath, row):
    file_exists = os.path.isfile(filepath)
    with open(filepath, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Username'])  # Write header if file is new
        writer.writerow(row)

# --- Check if Username Exists in CSV ---
def username_exists_in_csv(filepath, username):
    if not os.path.isfile(filepath):
        return False
    with open(filepath, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[-1] == username:
                return True
    return False

# --- Hardcoded Proxies ---
def load_proxies():
    return [
        "79.121.102.227:8080",
        "13.80.134.180:80",
        "133.18.234.13:80",
        "101.32.14.101:1080"
    ]

# --- Fetch Etoro Data for User ---
def fetch_etoro_data_for_user(username, instrument_map, proxies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.etoro.com/',
        'Origin': 'https://www.etoro.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers',
    }

    portfolio_csv_filepath = 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv'
    username_csv_filepath = 'AutomatingEtoroPosts/etoro_csv_contents/username.csv'
    cid_mapping_filepath = 'AutomatingEtoroPosts/etoro_csv_contents/cid_mapping.json'

    print(f"Processing username: {username}")

    if username_exists_in_csv(portfolio_csv_filepath, username):
        print(f"Username {username} already exists in portfolio_data.csv, skipping portfolio fetch.")
        return False
    else:
        for proxy in proxies:
            session = requests.Session()
            session.headers.update(headers)
            session.proxies.update({
                'http': proxy,
                'https': proxy,
            })

            try:
                user_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
                response = session.get(user_url)
                if response.status_code == 404:
                    print(f"Error: Username {username} does not exist on eToro.")
                    return False
                elif response.status_code != 200:
                    print(f"Error: Unable to fetch data for {username}, HTTP Status Code: {response.status_code}. It's possible that the proxy is blocked or the user is private.") 
                    continue

                user_data = response.json()
                realCID = user_data.get("realCID")
                gcid = user_data.get("gcid")
                demoCID = user_data.get("demoCID")

                if not realCID or not gcid or not demoCID:
                    print(f"Error: Missing data for {username}")
                    return False

                # Update cid_mapping.json
                cid_mapping = load_cid_mapping(cid_mapping_filepath)
                cid_mapping[username] = realCID
                save_cid_mapping(cid_mapping_filepath, cid_mapping)

                portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={realCID}"
                portfolio_response = session.get(portfolio_url)
                if portfolio_response.status_code == 403:
                    print(f"Error: Problem loading Portfolio for username {username}. It's possible that the proxy is blocked or the user is private ... Skipping.")
                    return False
                if portfolio_response.status_code != 200:
                    print(f"Error fetching portfolio data for {username}: HTTP Status Code: {portfolio_response.status_code}")
                    continue

                portfolio_data = portfolio_response.text
                portfolio_data_json = json.loads(portfolio_data)

                user_portfolio = []
                for position in portfolio_data_json.get("AggregatedPositions", []):
                    instrument_id = position.get("InstrumentID", "N/A")
                    ticker_name = instrument_map.get(str(instrument_id), "Unknown Ticker")
                    user_portfolio.append({
                        "InstrumentID": instrument_id,
                        "Ticker": ticker_name,
                        "Direction": position.get("Direction", "N/A"),
                        "Invested": position.get("Invested", "N/A"),
                        "NetProfit": position.get("NetProfit", "N/A"),
                        "Value": position.get("Value", "N/A"),
                        "Username": username
                    })

                add_json_to_csv({username: user_portfolio}, portfolio_csv_filepath, instrument_map)
                break  # Exit loop if successful
            except Exception as e:
                print(f"Error with proxy {proxy}: {e}")

    # Update username.csv
    if not username_exists_in_csv(username_csv_filepath, username):
        append_to_csv(username_csv_filepath, [username])
        return True
    return False

def main():
    instrument_map = load_instrument_map()
    proxies = load_proxies()

    # Set up Selenium WebDriver
    driver_path = "C:/Users/aiden/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    options = Options()
    options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-data-dir=C:/Users/aiden/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-software-rasterizer")

    service = Service(driver_path, log_path="NUL")
    driver = webdriver.Chrome(service=service, options=options)

    user_count = 0

    try:
        while True:
            driver.switch_to.window(driver.window_handles[-1])  # Switch to the latest opened tab
            current_url = driver.current_url
            if "https://www.etoro.com/people/" in current_url:
                username = current_url.split("https://www.etoro.com/people/")[1].split('/')[0]
                if fetch_etoro_data_for_user(username, instrument_map, proxies):
                    user_count += 1
                    print(f"Users added in this run: {user_count}")
            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        print("Script terminated by user.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()