import json
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

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

# --- CAPTCHA Handling ---
def check_for_captcha(driver):
    try:
        captcha_element = driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
        if captcha_element:
            print("CAPTCHA detected! Please resolve the CAPTCHA manually and re-run the script.")
            driver.quit()
            exit()
    except NoSuchElementException:
        # No CAPTCHA detected, proceed with the script
        pass

# --- Fetching Data ---
def fetch_etoro_data():
    with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
        instrument_map = json.load(f)
    
    try:
        with open('AutomatingEtoroPosts/mapping/cid_mapping.json', 'r') as f:
            cid_mapping = json.load(f)
    except FileNotFoundError:
        cid_mapping = {}
    
    with open('AutomatingEtoroPosts/etoro_csv_contents/etoro_usernames.csv', 'r') as f:
        usernames = [line.strip() for line in f]

    # Filter out usernames that already have cached realCID in cid_mapping
    new_usernames = [username for username in usernames if username not in cid_mapping]
    
    if not new_usernames:
        print("No new usernames found to process.")
        return

    driver = setup_browser()

    try:
        # Open portfolio_data.csv in append mode, create file if it doesn't exist
        with open('AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Check if file is empty to write headers once
            file.seek(0, 2)  # Move to end of file
            if file.tell() == 0:  # File is empty, write headers
                writer.writerow(["InstrumentID", "Ticker", "Direction", "Invested", "NetProfit", "Value", "Username"])

            for username in new_usernames:
                print(f"Processing {username}...")
                user_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
                driver.get(user_url)
                time.sleep(3)
                check_for_captcha(driver)

                try:
                    real_cid_element = driver.find_element(By.XPATH, "//pre[contains(text(), 'realCID')]")
                    real_cid = real_cid_element.text
                    if real_cid:
                        try:
                            real_cid_data = json.loads(real_cid)
                            real_cid_value = real_cid_data.get("realCID")
                            cid_mapping[username] = real_cid_value
                            print(f"Extracted realCID for {username}: {real_cid_value}")
                        except json.JSONDecodeError:
                            print(f"Failed to decode realCID JSON for {username}. Raw response: {real_cid}")
                            continue
                    else:
                        print(f"Failed to extract realCID for {username}.")
                        continue
                except Exception as e:
                    print(f"Error extracting realCID for {username}: {e}")
                    continue

                portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={real_cid_value}"
                driver.get(portfolio_url)
                time.sleep(3)
                check_for_captcha(driver)

                try:
                    portfolio_data_element = driver.find_element(By.XPATH, "//pre[contains(text(), '{')]")
                    portfolio_data = portfolio_data_element.text
                    print(f"Collecting portfolio data for {username}:")
                    try:
                        portfolio_data_json = json.loads(portfolio_data)
                        print(f"Successfully parsed portfolio data for {username}.")
                    except json.JSONDecodeError:
                        print(f"Failed to parse portfolio data as JSON for {username}. Check if the response is valid JSON.")
                        print(portfolio_data)
                        continue

                    # Process and write portfolio data
                    for position in portfolio_data_json.get("AggregatedPositions", []):
                        instrument_id = position.get("InstrumentID", "N/A")
                        ticker_name = instrument_map.get(str(instrument_id), "Unknown Ticker")
                        writer.writerow([instrument_id, ticker_name, position.get("Direction", "N/A"),
                                         position.get("Invested", "N/A"), position.get("NetProfit", "N/A"),
                                         position.get("Value", "N/A"), username])
                    print(f"Step 3: Portfolio data for {username} saved to portfolio_data.csv!")

                except Exception as e:
                    print(f"Error fetching portfolio data for {username}: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Save the updated CID mapping
        with open('AutomatingEtoroPosts/mapping/cid_mapping.json', 'w') as f:
            json.dump(cid_mapping, f, indent=4)

        driver.quit()

if __name__ == "__main__":
    fetch_etoro_data()
