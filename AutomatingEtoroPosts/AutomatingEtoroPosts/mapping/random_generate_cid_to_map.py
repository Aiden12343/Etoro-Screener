import json
import random
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException  # Import exception
import csv
from selenium.webdriver.common.by import By

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

# --- Fetch Data from URL ---
def fetch_cid_mapping_with_selenium(driver, cid_list):
    url = f"https://www.etoro.com/api/logininfo/v1.1/aggregatedInfo?cidList={cid_list}&avatar=true&realcid=true&client_request_id=d49bc69b-146b-422b-819e-3c8233cc5369"
    try:
        driver.get(url)
        time.sleep(3)
        try:
            raw_data = driver.find_element(By.TAG_NAME, "pre").text
        except NoSuchElementException:
            print("CAPTCHA detected or element not found. Ending script.")
            exit(1) 
        data = json.loads(raw_data)
        if "Users" not in data:
            print("Error: 'Users' key not found in the API response.")
            return {}
        cid_mapping = {}
        for user in data["Users"]:
            if user.get("firstName") is not None:
                cid_mapping[user["username"]] = user["realCID"]

        return cid_mapping
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}

# --- Update CID Mapping File ---
def update_cid_mapping(new_mapping):
    mapping_path = "AutomatingEtoroPosts/mapping/cid_mapping.json"
    os.makedirs(os.path.dirname(mapping_path), exist_ok=True)

    if os.path.exists(mapping_path):
        with open(mapping_path, "r") as file:
            existing_mapping = json.load(file)
    else:
        existing_mapping = {}

    existing_mapping.update(new_mapping)

    with open(mapping_path, "w") as file:
        json.dump(existing_mapping, file, indent=4)
    print(f"CID mapping updated. Total mappings: {len(existing_mapping)}")
    return set(existing_mapping.values())

# --- Add Username to CSV ---
def add_username_to_csv(username, csv_file="AutomatingEtoroPosts/etoro_csv_contents/etoro_usernames.csv"):
    try:
        with open(csv_file, "r", newline="") as f:
            reader = csv.reader(f)
            if not any(row for row in reader):
                with open(csv_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Username"])
    except FileNotFoundError:
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Username"])

    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username])

# --- Main Script ---
def main():
    target_mappings = 50
    valid_mappings = 0
    generated_uids = set()

    driver = setup_browser()

    try:
        mapping_path = "AutomatingEtoroPosts/mapping/cid_mapping.json"
        if os.path.exists(mapping_path):
            with open(mapping_path, "r") as file:
                existing_mapping = json.load(file)
            stored_uids = set(existing_mapping.values())
        else:
            stored_uids = set()

        print(f"Loaded {len(stored_uids)} existing UIDs.")
        while valid_mappings < target_mappings:
            cid_list = []
            while len(cid_list) < 100:
                uid = str(random.randint(10000000, 99999999))
                if uid not in generated_uids and uid not in stored_uids:
                    cid_list.append(uid)
                    generated_uids.add(uid)
            print(f"Generated CID list: {cid_list}")
            new_mapping = fetch_cid_mapping_with_selenium(driver, ",".join(cid_list))
            if new_mapping:
                print(f"Found valid mappings: {new_mapping}")
                valid_mappings += len(new_mapping)
                stored_uids = update_cid_mapping(new_mapping)
                for username in new_mapping:
                    add_username_to_csv(username)
            else:
                print("No valid mappings found. Retrying...")
        print(f"Successfully collected {target_mappings} valid mappings.")
    finally:
        driver.quit()
if __name__ == "__main__":
    main()
