# --- Imports ---
import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Browser Setup ---
def setup_browser():
    driver_path = "C:/Users/aiden/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    options = Options()
    options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-data-dir=C:/Users/aiden/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")


    service = Service(driver_path, log_path="NUL")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- Wait Function ---
def wait_for_element(driver, by, value, timeout=15):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"Timed out waiting for element: {value}")
        return None

# --- Scrape Data ---
def scrape_portfolio(driver, username):
    url = f"https://www.etoro.com/people/{username}/portfolio"
    driver.get(url)

    # Wait for the portfolio table header to load
    header_element = wait_for_element(
        driver,
        By.CSS_SELECTOR,
        "div[automation-id='cd-public-portfolio-table-header-first-cell']",
        timeout=15
    )
    if not header_element:
        print(f"Portfolio header not found for {username}. Skipping.")
        return []

    # Extract the number of assets from the header text
    header_text = header_element.text
    num_assets = int(header_text.split('(')[-1].split(')')[0])
    print(f"User {username} has {num_assets} assets in their portfolio.")

    # Initialize results
    portfolio_data = []

    # Wait for the table rows to load
    wait_for_element(driver, By.CSS_SELECTOR, "div.et-table-row-main", timeout=30)

    # Locate all rows dynamically
    rows = driver.find_elements(By.CSS_SELECTOR, "div.et-table-row-main")
    print(f"Found {len(rows)} rows in the portfolio table.")

    if len(rows) == 0:
        print(f"No rows found for {username}. Skipping.")
        return []

    for row_index, row in enumerate(rows):
        try:
            print(f"\n--- Processing Row {row_index + 1} ---")
            raw_text = row.text
            print(f"Raw row text: {raw_text}")

            # Split the raw text into lines
            lines = raw_text.split('\n')
            if len(lines) < 6:
                print(f"Row {row_index + 1} does not have the expected format. Skipping.")
                continue

            # Extract relevant values from the lines
            ticker = lines[0].strip()
            ticker_long_form = lines[1].strip()
            direction = lines[2].strip()
            exposure = lines[3].strip().replace('<', '')
            pl = lines[4].strip().replace('<', '')
            total_value = lines[5].strip().replace('<', '')

            # Append data to portfolio_data
            portfolio_data.append({
                "Ticker": ticker,
                "Ticker_Long_Form": ticker_long_form,
                "Direction": direction,
                "Exposure (%)": float(exposure.strip('%')),
                "P/L (%)": float(pl.strip('%')),
                "Total Value (%)": float(total_value.strip('%')),
                "Username": username
            })

        except Exception as e:
            print(f"Error processing row {row_index + 1}: {str(e)}")
            continue

    # Write to CSV
    with open(f'AutomatingEtoroPosts/user_portfolio_csv_results.csv/{username}_portfolio.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Ticker", "Ticker_Long_Form", "Direction", "Exposure (%)", "P/L (%)", "Total Value (%)", "Username"])
        for data in portfolio_data:
            writer.writerow([data["Ticker"], data["Ticker_Long_Form"], data["Direction"], data["Exposure (%)"], data["P/L (%)"], data["Total Value (%)"], data["Username"]])

    print("CSV file created successfully!")
    return portfolio_data

# --- Main Function ---
def main():
    input_csv = "AutomatingEtoroPosts/etoro_usernames.csv"
    output_csv = "AutomatingEtoroPosts/portfolio_cleaned.csv"

    with open(input_csv, "r") as file:
        usernames = [row[0] for row in csv.reader(file) if row]

    driver = setup_browser()
    all_portfolio_data = []

    try:
        for username in usernames:
            print(f"Processing portfolio for user: {username}")
            portfolio_data = scrape_portfolio(driver, username)
            all_portfolio_data.extend(portfolio_data)

        if all_portfolio_data:
            pd.DataFrame(all_portfolio_data).to_csv(output_csv, index=False)
            print("Portfolio data updated successfully!")
        else:
            print("No portfolio data collected.")

    finally:
        driver.quit()

# --- Run Script ---
if __name__ == "__main__":
    main()
