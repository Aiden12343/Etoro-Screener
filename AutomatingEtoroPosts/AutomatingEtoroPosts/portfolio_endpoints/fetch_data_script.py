import sys
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from selenium.common.exceptions import NoSuchElementException

# Load InstrumentID to Ticker mapping from a file
def load_instrument_map():
    try:
        with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
            instrument_map = json.load(f)
    except FileNotFoundError:
        instrument_map = {}  # Default to an empty map if the file doesn't exist
    return instrument_map

# Check if the username already exists in the CSV file
def username_exists(username):
    try:
        with open('AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[-1] == username:  # Check if username exists in the last column
                    return True
    except FileNotFoundError:
        return False  # If file doesn't exist, it means no data has been collected yet
    return False

def setup_browser():
    # Browser setup
    driver_path = "C:/Users/aiden/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-data-dir=C:/Users/aiden/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def check_for_captcha(driver):
    try:
        captcha_element = driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
        if captcha_element:
            print("CAPTCHA detected! Please resolve it.")
            driver.quit()
            exit()
    except NoSuchElementException:
        pass

def fetch_etoro_data_for_user(username, instrument_map):
    driver = setup_browser()

    try:
        user_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
        driver.get(user_url)
        time.sleep(3)
        check_for_captcha(driver)

        # Extract CID and fetch portfolio
        real_cid_element = driver.find_element(By.XPATH, "//pre[contains(text(), 'realCID')]")
        real_cid = real_cid_element.text
        real_cid_data = json.loads(real_cid)
        real_cid_value = real_cid_data.get("realCID")

        # Fetch portfolio data
        portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={real_cid_value}"
        driver.get(portfolio_url)
        time.sleep(3)
        check_for_captcha(driver)

        portfolio_data_element = driver.find_element(By.XPATH, "//pre[contains(text(), '{')]")
        portfolio_data = portfolio_data_element.text
        portfolio_data_json = json.loads(portfolio_data)

        # Append the portfolio data to the existing CSV
        with open('AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Only write headers if the file is empty
            if file.tell() == 0:
                writer.writerow(["InstrumentID", "Ticker", "Direction", "Invested", "NetProfit", "Value", "Username"])

            for position in portfolio_data_json.get("AggregatedPositions", []):
                instrument_id = position.get("InstrumentID", "N/A")
                
                # Debugging: Check InstrumentID and mapping
                print(f"InstrumentID: {instrument_id}")
                ticker_name = instrument_map.get(str(instrument_id), "Unknown Ticker")
                print(f"Mapped Ticker: {ticker_name}")  # Debug the mapping

                writer.writerow([instrument_id, ticker_name, position.get("Direction", "N/A"), position.get("Invested", "N/A"), position.get("NetProfit", "N/A"), position.get("Value", "N/A"), username])

    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Load InstrumentID to Ticker mapping
    instrument_map = load_instrument_map()

    # Accept the username as a command-line argument
    username = sys.argv[1]

    # Check if data for the user already exists in the CSV
    if username_exists(username):
        print(f"Data for {username} already exists, skipping data collection.")
    else:
        fetch_etoro_data_for_user(username, instrument_map)
