import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up browser using Selenium
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

# Extract and save cookies
def save_cookies(driver, cookies_file):
    try:
        cookies = driver.get_cookies()
        with open(cookies_file, "w") as file:
            json.dump(cookies, file)
        print("Cookies saved successfully.")
    except Exception as e:
        print("Failed to save cookies:", e)

# Load cookies into browser session
def load_cookies(driver, cookies_file):
    with open(cookies_file, "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    print("Cookies loaded successfully.")

# Prepare cookies manually (or extract them using Selenium)
def prepare_cookies():
    # Add your list of cookies here
    cookies = [
        {"name": "OptanonAlertBoxClosed", "value": "2024-12-16T00:31:53.857Z", "domain": ".etoro.com", "path": "/"},
        {"name": "_gcl_au", "value": "1.1.1004025800.1734309114", "domain": ".etoro.com", "path": "/"},
        {"name": "OptanonConsent", "value": "isGpcEnabled=0&datestamp=Mon+Dec+16+2024+00%3A31%3A53+GMT%2B0000+(Greenwich+Mean+Time)&version=202410.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=4661357a-75fa-43e8-805e-a4fd774f4f0a&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1", "domain": ".etoro.com", "path": "/"},
        {"name": "etoroHPRedirect", "value": "1", "domain": ".etoro.com", "path": "/"},
        {"name": "_hjSessionUser_1871831", "value": "eyJpZCI6IjhlYTg2NWU2LWM4MDAtNWQ3YS04MjY3LWY3ZGMxZDIxNWFlMCIsImNyZWF0ZWQiOjE3MzQzMDkxMTIzNjMsImV4aXN0aW5nIjp0cnVlfQ==", "domain": ".etoro.com", "path": "/"},
        # Add all other cookies similarly
        {"name": "_ga", "value": "GA1.2.434524226.1726937789", "domain": ".etoro.com", "path": "/"},
        {"name": "_gat", "value": "1", "domain": ".etoro.com", "path": "/"},
        {"name": "_ga_B0NS054E7V", "value": "GS1.1.1734620212.9.1.1734620446.51.0.0", "domain": ".etoro.com", "path": "/"},
        {"name": "_uetsid", "value": "7b939070be1911efa6f31797f5501dc4", "domain": ".etoro.com", "path": "/"},
        {"name": "_uetvid", "value": "1e00fe70bb4511efb9bd3f32ccdd4735", "domain": ".etoro.com", "path": "/"},
        # Continue adding all necessary cookies here
    ]
    return cookies

# Send POST request using cookies and access token for authentication
def post_comment_using_api(cookies, access_token=None):
    # Endpoint URL for posting comment (replace with actual ID)
    url = "https://www.etoro.com/api/edm-streams/v1/feed/discussion/a74a2f70-bd8d-11ef-8080-80007d4484a0/comment?client_request_id=72ae62d0-43d8-49d7-90ee-7e70fb6eef13"

    # Prepare cookies from Selenium
    cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

    # Set headers
    headers = {
        "Content-Type": "application/json",
    }

    # If access token is available, add to headers
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    # Data to send (the message to post)
    data = {
        "message": "This is a test comment.",
    }

    # Send POST request with cookies and headers
    response = requests.post(url, headers=headers, cookies=cookies_dict, json=data)

    if response.status_code == 200:
        print("Comment posted successfully.")
    else:
        print(f"Failed to post comment: {response.status_code}")
        print(response.json())  # Check response message for error details

# Main program
def main():
    driver = setup_browser()
    driver.get("https://www.etoro.com")  # Open eToro to interact and load cookies

    # Step 1: Prepare and load cookies
    cookies = prepare_cookies()  # Or load cookies from previous session using save/load
    save_cookies(driver, "etoro_cookies.json")  # Save cookies to a file
    load_cookies(driver, "etoro_cookies.json")  # Load cookies

    # Step 2: Post the comment using the extracted cookies
    post_comment_using_api(cookies)

    # Close browser
    driver.quit()

if __name__ == "__main__":
    main()
