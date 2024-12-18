import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
def fetch_cid_mapping_from_url(driver, url):
    """
    Fetch JSON data from the provided URL and extract public accounts.
    """
    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load (adjust if needed)

        # Extract JSON response from the page source
        raw_data = driver.find_element(By.TAG_NAME, "pre").text
        data = json.loads(raw_data)

        if "Users" not in data:
            print("Error: 'Users' key not found in the API response.")
            return {}

        # Filter out private accounts based on "firstName": null
        cid_mapping = {}
        for user in data["Users"]:
            if user.get("firstName") is not None:  # Check if firstName is not null
                cid_mapping[user["username"]] = user["realCID"]

        return cid_mapping

    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}

# --- Update CID Mapping File ---
def update_cid_mapping(new_mapping):
    """
    Updates the CID mapping file with new data, ensuring no duplicates.
    """
    mapping_path = "AutomatingEtoroPosts/mapping/cid_mapping.json"
    os.makedirs(os.path.dirname(mapping_path), exist_ok=True)

    # Load existing mapping if it exists
    if os.path.exists(mapping_path):
        with open(mapping_path, "r") as file:
            existing_mapping = json.load(file)
    else:
        existing_mapping = {}

    # Find the difference between new and existing mappings
    new_cids = {k: v for k, v in new_mapping.items() if k not in existing_mapping}

    if not new_cids:
        print("No new CIDs.")
        return 0  # Indicates no new usernames mapped

    # Merge new mapping into existing mapping
    existing_mapping.update(new_cids)

    # Save the updated mapping back to the file
    with open(mapping_path, "w") as file:
        json.dump(existing_mapping, file, indent=4)
    print("CID mapping updated successfully.")
    return len(new_cids)  # Return the count of new usernames mapped

# --- Add Username to CSV ---
def add_username_to_csv(username, csv_file="AutomatingEtoroPosts/etoro_csv_contents/etoro_usernames.csv"):
    """Add the username to the CSV file if not already present."""
    try:
        with open(csv_file, "r", newline="") as f:
            reader = csv.reader(f)
            if not any(row for row in reader):  # Check if file is empty
                with open(csv_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Username"])  # Write header if file is empty
    except FileNotFoundError:
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Username"])  # Write header if file doesn't exist

    # Append the username to the CSV
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username])

# --- Main Script ---
def main():
    # Ask user for the URL
    url = input("Please enter the URL to scan: ").strip()

    # Validate URL input
    if not url.startswith("http"):
        print("Invalid URL. Please ensure the URL starts with 'http' or 'https'.")
        return

    # Setup browser
    driver = setup_browser()

    try:
        # Fetch CID mapping
        new_mapping = fetch_cid_mapping_from_url(driver, url)

        if new_mapping:
            # Update mapping and get the count of new usernames mapped
            new_user_count = update_cid_mapping(new_mapping)

            # Add new usernames to the CSV
            for username in new_mapping:
                add_username_to_csv(username)

            # Display the count of successfully mapped usernames
            print(f"Total usernames successfully mapped: {new_user_count}")
        else:
            print("No valid mappings found.")
    finally:
        # Quit the browser
        driver.quit()

if __name__ == "__main__":
    main()
