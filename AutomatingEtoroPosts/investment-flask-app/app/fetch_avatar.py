import requests
import csv
import os

def load_proxies():
    return [
        "130.162.180.254:8888",
        "101.255.166.242:8080",
        "13.80.134.180:80",
        "133.18.234.13:80",
        "101.32.14.101:1080"
    ]

def fetch_avatar_url(endpoint_url, username):
    try:
        proxies = load_proxies()
        proxy = {'http': proxies[0], 'https': proxies[0]}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.etoro.com/',
            'Origin': 'https://www.etoro.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
        }

        response = requests.get(endpoint_url, headers=headers, proxies=proxy)
        response.raise_for_status()
        user_info = response.json()

        # Debugging statement to print the JSON response
        print(f"User info JSON response: {user_info}")

        # Check if 'avatars' key exists and is not empty
        if 'avatars' in user_info and user_info['avatars']:
            avatar_url = user_info['avatars'][0]['url']
            # Debugging statement to print the extracted avatar URL
            print(f"Extracted avatar URL: {avatar_url}")
        else:
            avatar_url = None
            print("No avatars key found or avatars list is empty.")

        # Save to CSV
        csv_file = 'AutomatingEtoroPosts/investment-flask-app/images/user_avatars.csv'
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['username', 'avatar_url'])
            writer.writerow([username, avatar_url])

        return avatar_url
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    username = input("Please enter the username: ")
    endpoint_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
    avatar_url = fetch_avatar_url(endpoint_url, username)
    if avatar_url:
        print(f"Avatar URL: {avatar_url}")
    else:
        print("No avatar URL found.")