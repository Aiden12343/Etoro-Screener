# --- Imports ---
import time
import logging
import os
import sys
import yfinance                          as yf
import numpy                             as np
import pandas                            as pd
from   datetime                          import datetime
from   selenium                          import webdriver
from   selenium.webdriver.chrome.service import Service
from   selenium.webdriver.chrome.options import Options
from   selenium.webdriver.common.by      import By
from   selenium.webdriver.support.ui     import WebDriverWait
from   selenium.webdriver.support        import expected_conditions as EC
from   selenium.webdriver.common.keys    import Keys
import pyautogui  # Importing pyautogui


# --- Logging and Environment Setup ---
logging.disable(logging.WARNING)  # Disable warnings and below (INFO, DEBUG)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # TensorFlow: Suppress all but critical logs
sys.stderr = open("error_log.txt", "w")  # Redirect errors to a log file
sleep_seconds = 86400

logging.basicConfig(
    filename="trade_log.txt", 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s'
)

# Constants for algorithm
emalen = 9
basePeriods = 13 
conversionPeriods = 8
laggingSpan2Periods = 26
displacement = 13

# Algorithm Logic
def donchian(data, period):
    return (data['Low'].rolling(window=period).min() + data['High'].rolling(window=period).max()) / 2

def calculate_ichimoku(data):
    data['ConversionLine'] = donchian(data, conversionPeriods)
    data['BaseLine']       = donchian(data, basePeriods)
    data['LeadLine1']      = (data['ConversionLine'] + data['BaseLine']) / 2
    data['LeadLine2']      = donchian(data, laggingSpan2Periods)

    data['CloudMin'] = np.minimum(
        data['LeadLine1'].shift(displacement - 1),
        data['LeadLine2'].shift(displacement - 1)
    )
    data['CloudMax'] = np.maximum(
        data['LeadLine1'].shift(displacement - 1),
        data['LeadLine2'].shift(displacement - 1)
    )

    data['Trend'] = np.where(data['Close'] > data['CloudMax'], 1,
                             np.where(data['Close'] < data['CloudMin'], -1, 0))

    data['Oscline'] = np.where(data['Trend'] == 1,
                                 data['Close'] - data['CloudMin'],
                                 data['Close'] - data['CloudMax'])

    data['Lagging'] = data['Oscline'] + np.where(
        data['Trend'] == 1,
        np.maximum(data['Close'] - data['CloudMax'].shift(displacement - 1), 0),
        np.minimum(data['Close'] - data['CloudMin'].shift(displacement - 1), 0)
    )

    data['ConvBase'] = data['Lagging'] + np.where(
        data['Trend'] == 1,
        np.maximum(data['ConversionLine'] - data['BaseLine'], 0),
        np.minimum(data['ConversionLine'] - data['BaseLine'], 0)
    )

    data['Cloud'] = data['ConvBase'] + np.where(
        data['Trend'] == 1,
        np.maximum(data['LeadLine1'] - data['LeadLine2'], 0),
        np.minimum(data['LeadLine1'] - data['LeadLine2'], 0)
    )

    data['EMA_Line'] = data['Cloud'].ewm(span=emalen).mean()

    data['Signal'] = (data['EMA_Line'] > data['EMA_Line'].shift(1)) & \
        (data['EMA_Line'] < 0) & \
        (data['EMA_Line'].shift(1) < data['EMA_Line'].shift(2)) & \
        (data['EMA_Line'].shift(1) < 0)
    
    return data

# --- Browser Setup ---
def setup_browser():
    driver_path = "C:/Users/aiden/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe" 
    options = Options()
    options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--disable-logging")  # Disable logging
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-data-dir=C:/Users/aiden/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer

    service = Service(driver_path, log_path="NUL")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- Trading Functions ---

# Function to check if the buy signal is TRUE
def check_buy_signal(ticker):
    data = yf.download(ticker, period="3mo", interval="1d")  # Adjust interval as needed
    data = calculate_ichimoku(data)
    if data['Signal'].iloc[-1]:
        return True
    return False

def is_valid_ticker(ticker, driver):
    url = f'https://www.etoro.com/markets/{ticker}'
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(2)  # Allow the page to load
    
    # Check if the "Sign Up" button exists, indicating that the user is not signed in
    try:
        sign_up_button = driver.find_element(By.XPATH, '//a[contains(@class, "et-button-signup")]')
        if sign_up_button.is_displayed():
            print("Error: User is not signed in to eToro. Please sign in and restart the script.")
            driver.quit()  # Quit the browser
            exit()         # Terminate the script
    except:
        # No "Sign Up" button found, meaning the user is signed in
        pass
    
    # Check if the ticker redirects to the homepage (invalid ticker)
    current_url = driver.current_url
    if current_url == "https://www.etoro.com/home":
        print(f"Ticker {ticker} is invalid (redirected to homepage). Skipping...")
        return False
    else:
        print(f"Ticker {ticker} is valid.")
        return True

def log_trade(ticker, amount):
    """Log trade details (timestamp, asset, amount) to a text file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Capture the timestamp
    with open("trade_log.txt", "a") as f:  # Open file in append mode
        f.write(f"Timestamp: {timestamp}, Asset: {ticker}, Amount: ${amount}\n")
        print(f"Trade logged: {timestamp}, Asset: {ticker}, Amount: ${amount}")

def perform_trade(ticker, amount, driver):
    """Perform a trade on eToro for the given ticker and amount."""
    url = f'https://www.etoro.com/markets/{ticker}'
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[@automation-id="trade-button"]')))

    # Click trade button
    driver.find_element(By.XPATH, '//div[@automation-id="trade-button"]').click()
    time.sleep(2)

    # Enter amount
    amount_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@automation-id="open-position-amount-input-amount"]'))
    )
    amount_input.clear()
    amount_input.send_keys(str(amount))
    amount_input.send_keys(Keys.ENTER)
    time.sleep(2)

    # Confirm trade
    buy_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@automation-id="open-position-by-value-submit-button"]'))
    )
    buy_button.click()
    time.sleep(3)

    # Log the trade after confirming
    log_trade(ticker, amount)

def verify_and_switch_account(driver, desired_account):
    """Verify the current account and switch to the desired account if necessary."""
    current_account = check_account_type(driver)
    print(f"Current account type: {current_account}")
    
    if current_account == 'unknown':
        print("Error: Could not determine the account type.")
        driver.quit()
        exit()

    if current_account != desired_account:
        print(f"Switching to {desired_account} account...")

        try:
            if desired_account == 'real' and current_account != 'real':
                # Switch to real account
                switch_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="icon-arrow-right to-real ng-star-inserted"]'))
                )
                switch_button.click()
                
                # Wait for and click the "Go real" button
                go_real_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="toggle-account-button"]'))
                )
                go_real_button.click()
                
                print("Successfully switched to real account.")

            elif desired_account == 'virtual' and current_account != 'virtual':
                # Switch to virtual account
                switch_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="icon-arrow-right to-virtual ng-star-inserted"]'))
                )
                switch_button.click()
                
                # Wait for and click the "Go virtual" button
                go_virtual_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="toggle-account-button"]'))
                )
                go_virtual_button.click()
                
                print("Successfully switched to virtual account.")
            
            # Wait for the account switch to complete
            print("Waiting for the account switch to complete...")
            time.sleep(15)  # Optional, wait for the page to stabilize

        except Exception as e:
            print(f"Error switching to {desired_account} account: {e}")
            driver.quit()  # Quit if switching fails
            exit()
    else:
        print(f"Account is already in {desired_account} mode. No switch needed.")


def check_account_type(driver):
    """Check the current account type (real or virtual)."""
    try:
        # Wait for the account amount section to be loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@automation-id="overview-amount"]'))
        )
        
        # Check if real account is visible
        real_account = driver.find_element(By.XPATH, '//div[@automation-id="overview-amount"]')
        if real_account and not 'amount-demo' in real_account.get_attribute('class'):
            return 'real'
    except Exception as e:
        print(f"Error while checking real account: {e}")
        pass

    try:
        # Check if virtual account is visible
        virtual_account = driver.find_element(By.XPATH, '//div[@automation-id="overview-amount"]')
        if virtual_account and 'amount-demo' in virtual_account.get_attribute('class'):
            return 'virtual'
    except Exception as e:
        print(f"Error while checking virtual account: {e}")
        pass

    return 'unknown'

# --- Main Execution Loop ---
if __name__ == "__main__":
    # Ask the user to specify the account type (real or virtual) before launching the browser
    while True:
        desired_account = input("Enter account type ('real' or 'virtual'): ").strip().lower()
        if desired_account in ['real', 'virtual']:
            break
        else:
            print("Invalid input. Please enter 'real' or 'virtual'.")

    # Switch to a new desktop before launching the browser
    pyautogui.hotkey('ctrl', 'win', 'd')  # Create a new desktop
    time.sleep(5)  # Wait a bit for the desktop to switch

    # Now, setup the browser after getting the account type
    driver = setup_browser()
    # After finishing, switch back to the original desktop

    # Switch to the desired account based on the user input
    verify_and_switch_account(driver, desired_account)  # Switch to the desired account
    pyautogui.hotkey('ctrl', 'win', 'left')  # Switch back to the original desktop

    account_type = check_account_type(driver)
    print(f"Trading with {account_type} account.")

    amount = 100  # Set trade amount

    # Load tickers from CSV
    try:
        tickers_df = pd.read_csv("AutomatingEtoroPosts\auto_trading\automate.tickers.csv")  
        tickers = tickers_df['Ticker'].tolist()
    except FileNotFoundError:
        print("CSV file 'automate_tickers.csv' not found. Exiting.")
        driver.quit()
        exit()

    try:
        while True:
            for ticker in tickers:
                print(f"Checking ticker: {ticker}...")

                if not is_valid_ticker(ticker, driver):
                    print(f"Skipping invalid ticker: {ticker}")
                    continue  

                try:
                    if check_buy_signal(ticker):
                        print(f"Buy signal detected for {ticker}. Initiating trade.")
                        perform_trade(ticker, amount, driver)
                    else:
                        print(f"No buy signal for {ticker}.")
                except Exception as e:
                    print(f"Error with ticker {ticker}: {e}")
                    continue 
            print(f"Sleeping for {sleep_seconds / 3600} hours")
            time.sleep(sleep_seconds)  # Sleep for one day
    except KeyboardInterrupt:
        print("Script interrupted by user. Exiting...")
    finally:
        driver.quit()

