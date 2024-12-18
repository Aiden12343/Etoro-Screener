import csv
import json
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# --- Browser Setup ---
def setup_browser():
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
    return driver

# --- Fetch User Portfolio Data ---
def fetch_user_portfolio(driver, username, instrument_map, cid_mapping):
    try:
        if username in cid_mapping:
            real_cid_value = cid_mapping[username]
        else:
            user_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
            driver.get(user_url)
            time.sleep(3)
            real_cid_element = driver.find_element(By.XPATH, "//pre[contains(text(), 'realCID')]")
            real_cid = real_cid_element.text
            real_cid_data = json.loads(real_cid)
            real_cid_value = real_cid_data.get("realCID")
            cid_mapping[username] = real_cid_value
        
        portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={real_cid_value}"
        driver.get(portfolio_url)
        time.sleep(3)

        portfolio_data_element = driver.find_element(By.XPATH, "//pre[contains(text(), '{')]")
        portfolio_data = portfolio_data_element.text
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
        
        return user_portfolio
    except Exception as e:
        print(f"Error fetching portfolio data for {username}: {e}")
        return []

# --- Sync Data Based on Timestamp ---
def sync_data():
    print("Stage 1: Reading existing portfolio data from timestamp.csv.")
    # Read timestamp data into a dictionary by username
    timestamp_mapping = {}
    with open('AutomatingEtoroPosts/etoro_csv_contents/timestamp.csv', mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:  # Ensure there are exactly two columns: username and timestamp
                username, timestamp_str = row
                timestamp_mapping[username] = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    # Load instrument mapping
    with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
        instrument_map = json.load(f)

    # Load the CID mapping
    try:
        with open('AutomatingEtoroPosts/mapping/cid_mapping.json', 'r') as f:
            cid_mapping = json.load(f)
    except FileNotFoundError:
        cid_mapping = {}

    # Get the current time for comparison
    current_time = datetime.now()

    # Prepare to update data
    updated_data = []
    users_to_update = {}

    # Check each user in timestamp_mapping and update if needed
    for username, timestamp in timestamp_mapping.items():
        # Check if the timestamp is more than 24 hours ago
        if current_time - timestamp > timedelta(hours=24):
            print(f"Stage 2: Data for {username} is outdated. Fetching new data.")
            users_to_update[username] = timestamp  # Mark for update

    # Open the browser
    print("Stage 3: Setting up browser.")
    driver = setup_browser()

    # Fetch updated data for users that need it
    for username in users_to_update.keys():
        user_portfolio = fetch_user_portfolio(driver, username, instrument_map, cid_mapping)
        if user_portfolio:
            # Update the user data and timestamp in the CSV (skip the timestamp column)
            for position in user_portfolio:
                updated_row = [position.get("InstrumentID", "N/A"),
                               position.get("Ticker", "Unknown Ticker"),
                               position.get("Direction", "N/A"),
                               position.get("Invested", "N/A"),
                               position.get("NetProfit", "N/A"),
                               position.get("Value", "N/A"),
                               username]  # No timestamp here
                updated_data.append(updated_row)
        else:
            print(f"Stage 4: No data found for {username}. Skipping user.")

    # Add users who do not need an update
    print("Stage 5: Writing updated data back to CSV.")
    with open('AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(updated_data)

    driver.quit()
    print("Stage 6: Sync process complete.")

if __name__ == "__main__":
    sync_data()
