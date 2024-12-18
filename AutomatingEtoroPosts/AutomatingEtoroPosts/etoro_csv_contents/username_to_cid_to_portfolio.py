import csv
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

# --- Terminal Color Codes ---
class TerminalColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"

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

# --- Add Timestamp to CSV ---
def add_timestamp_to_csv(username, timestamp, timestamp_file='timestamp.csv'):
    try:
        with open(timestamp_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([username, timestamp])
        print(f"{TerminalColors.GREEN}Timestamp added for user {username}.{TerminalColors.RESET}")
    except Exception as e:
        print(f"{TerminalColors.RED}Error adding timestamp: {e}{TerminalColors.RESET}")

# --- CAPTCHA Handling ---
def check_for_captcha(driver):
    try:
        captcha_element = driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
        if captcha_element:
            print(f"{TerminalColors.RED}CAPTCHA detected! Please resolve the CAPTCHA manually and re-run the script.{TerminalColors.RESET}")
            driver.quit()
            exit()
    except NoSuchElementException:
        pass  # No CAPTCHA detected, proceed with the script

# --- Add JSON Data to Portfolio CSV ---
# --- Add JSON Data to Portfolio CSV ---
def add_json_to_csv(json_data, csv_file_path, instrument_map):
    try:
        # Read the existing CSV to keep track of rows that need to be updated
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as file:
            existing_data = list(csv.reader(file))

        # Get the header from the first row (if any)
        header = existing_data[0] if existing_data else []

        # Create a list to hold the updated data, starting with the header (if it exists)
        updated_data = []
        if header:
            updated_data.append(header)

        # Create a set to keep track of usernames already in the CSV
        existing_usernames = set(row[-1] for row in existing_data[1:] if row)  # Skip the header row

        # Iterate through the provided JSON data and update or add rows
        for username, portfolio_data in json_data.items():
            # If the username does not exist in the CSV, we add new rows
            if username not in existing_usernames:
                print(f"{TerminalColors.YELLOW}Adding new rows for user: {username}{TerminalColors.RESET}")
                for position in portfolio_data:
                    instrument_id = position.get("InstrumentID", "N/A")
                    ticker_name = instrument_map.get(str(instrument_id), "Unknown Ticker")
                    updated_data.append([instrument_id, ticker_name, position.get("Direction", "N/A"),
                                         position.get("Invested", "N/A"), position.get("NetProfit", "N/A"),
                                         position.get("Value", "N/A"), username])
            else:
                # Update existing rows for the user
                for row in existing_data[1:]:  # Skip the header row
                    if row and row[-1] == username:  # If this row belongs to the user
                        # Replace the user's data with the updated data
                        for position in portfolio_data:
                            instrument_id = position.get("InstrumentID", "N/A")
                            ticker_name = instrument_map.get(str(instrument_id), "Unknown Ticker")
                            updated_data.append([instrument_id, ticker_name, position.get("Direction", "N/A"),
                                                 position.get("Invested", "N/A"), position.get("NetProfit", "N/A"),
                                                 position.get("Value", "N/A"), username])
                        break  # User found, no need to process further rows

        # Sort the data by the 'Username' column (last column)
        updated_data.sort(key=lambda x: x[-1])

        # Now, write the sorted updated data back to the CSV file, only if it doesn't overwrite the header
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(updated_data)

        print(f"{TerminalColors.GREEN}Successfully updated CSV data.{TerminalColors.RESET}")
    except Exception as e:
        print(f"{TerminalColors.RED}Error adding/updating CSV: {e}{TerminalColors.RESET}")



# --- Main Function to Fetch and Process Data ---
def fetch_etoro_data():
    print(f"{TerminalColors.CYAN}Stage 1: Loading instrument mapping from JSON.{TerminalColors.RESET}")
    with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
        instrument_map = json.load(f)

    print(f"{TerminalColors.CYAN}Stage 2: Loading user ID mappings.{TerminalColors.RESET}")
    try:
        with open('AutomatingEtoroPosts/mapping/cid_mapping.json', 'r') as f:
            cid_mapping = json.load(f)
    except FileNotFoundError:
        cid_mapping = {}

    with open('AutomatingEtoroPosts/mapping/private_cid_mapping.json', 'r') as f:
        private_cid_mapping = json.load(f)

    print(f"{TerminalColors.CYAN}Stage 3: Loading user list from CSV.{TerminalColors.RESET}")
    with open('AutomatingEtoroPosts/etoro_csv_contents/etoro_usernames.csv', 'r') as f:
        usernames = [line.strip() for line in f]

    driver = setup_browser()

    try:
        print(f"{TerminalColors.CYAN}Stage 4: Reading existing portfolio data from CSV.{TerminalColors.RESET}")
        with open('AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', mode="r", newline="", encoding="utf-8") as file:
            existing_data = list(csv.reader(file))

        new_data = {}

        for username in usernames:
            print(f"{TerminalColors.YELLOW}Stage 5: Processing user: {username}{TerminalColors.RESET}")

            if username in cid_mapping:
                real_cid_value = cid_mapping[username]
                print(f"{TerminalColors.YELLOW}Stage 6: Using cached realCID for {username}: {real_cid_value}{TerminalColors.RESET}")
            else:
                user_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
                print(f"{TerminalColors.YELLOW}Stage 7: Loading endpoint {user_url}{TerminalColors.RESET}")
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
                            print(f"{TerminalColors.YELLOW}Stage 8: Extracted realCID for {username}: {real_cid_value}{TerminalColors.RESET}")
                        except json.JSONDecodeError:
                            print(f"{TerminalColors.RED}Stage 9: Failed to decode realCID JSON for {username}.{TerminalColors.RESET}")
                            continue
                except Exception as e:
                    print(f"{TerminalColors.RED}Stage 10: Error extracting realCID for {username}: {e}{TerminalColors.RESET}")
                    continue

            portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={real_cid_value}"
            print(f"{TerminalColors.YELLOW}Stage 11: Loading endpoint {portfolio_url}{TerminalColors.RESET}")
            driver.get(portfolio_url)
            time.sleep(3)
            check_for_captcha(driver)

            try:
                portfolio_data_element = driver.find_element(By.XPATH, "//pre[contains(text(), '{')]")
                portfolio_data = portfolio_data_element.text
                print(f"{TerminalColors.YELLOW}Stage 12: Collecting portfolio data for {username}.{TerminalColors.RESET}")

                try:
                    portfolio_data_json = json.loads(portfolio_data)
                    print(f"{TerminalColors.GREEN}Stage 13: Successfully parsed portfolio data for {username}.{TerminalColors.RESET}")

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

                    new_data[username] = user_portfolio
                    print(f"{TerminalColors.GREEN}Stage 14: Processed portfolio for {username}.{TerminalColors.RESET}")

                    # Save data after processing each user
                    add_json_to_csv(new_data, 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', instrument_map)

                    # Add timestamp for the username to timestamp.csv
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    add_timestamp_to_csv(username, timestamp)

                except json.JSONDecodeError:
                    print(f"{TerminalColors.RED}Stage 15: Failed to parse portfolio data as JSON for {username}. The raw data might not be valid JSON.{TerminalColors.RESET}")
                    print(f"Raw portfolio data for {username}: {portfolio_data}")
                    continue  # Skip this user and proceed with the next one

            except Exception as e:
                print(f"{TerminalColors.RED}Stage 16: Error fetching portfolio data for {username}: {e}{TerminalColors.RESET}")

        # Final save of data (although we are already saving after each user)
        print(f"{TerminalColors.CYAN}Stage 17: Final saving data to CSV.{TerminalColors.RESET}")
        add_json_to_csv(new_data, 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', instrument_map)

    except Exception as e:
        print(f"{TerminalColors.RED}Stage 18: Error: {e}{TerminalColors.RESET}")
    finally:
        print(f"{TerminalColors.CYAN}Stage 19: Saving mappings to disk.{TerminalColors.RESET}")
        with open('AutomatingEtoroPosts/mapping/cid_mapping.json', 'w') as f:
            json.dump(cid_mapping, f, indent=4)

        with open('AutomatingEtoroPosts/mapping/private_cid_mapping.json', 'w') as f:
            json.dump(private_cid_mapping, f, indent=4)

        driver.quit()

# --- Execute ---
fetch_etoro_data()
