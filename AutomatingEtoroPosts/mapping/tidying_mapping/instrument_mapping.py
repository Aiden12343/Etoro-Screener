from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time

# Browser setup function (from your setup)
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

# Function to fetch data and map InstrumentID to SymbolFull
def fetch_instrument_data():
    driver = setup_browser()
    driver.get("https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments")

    # Wait for the content to load (adjust time as needed)
    time.sleep(5)  # You may need to tweak this depending on the network speed and page load time

    # Extract the JSON data from the page's script tag or any other available method
    script_tag = driver.find_element(By.TAG_NAME, 'pre')  # The JSON might be in a <pre> tag
    json_data = script_tag.text

    # Parse the JSON data
    data = json.loads(json_data)
    
    # Create a dictionary to hold the InstrumentID to SymbolFull mapping
    instrument_mapping = {}

    # Loop through the "InstrumentDisplayDatas" to build the mapping
    for instrument in data.get("InstrumentDisplayDatas", []):
        instrument_id = instrument.get("InstrumentID")
        symbol_full = instrument.get("SymbolFull")
        
        if instrument_id and symbol_full:
            instrument_mapping[instrument_id] = symbol_full

    # Save the mapping to a file
    output_file = "AutomatingEtoroPosts/mapping/instrument_mapping.json"
    
    # Ensure the directory exists, create it if necessary
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the mapping to the file (overwrite if it already exists)
    with open(output_file, "w") as file:
        json.dump(instrument_mapping, file, indent=4)

    # Close the browser
    driver.quit()

    print(f"Mapping saved to {output_file}")

# Run the function
fetch_instrument_data()
