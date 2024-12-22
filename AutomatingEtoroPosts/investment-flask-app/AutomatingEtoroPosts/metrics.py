import requests
import csv
import os
import json

def load_proxies():
    return [
        "130.162.180.254:8888",
        "101.255.166.242:8080",
        "13.80.134.180:80",
        "133.18.234.13:80",
        "101.32.14.101:1080"
    ]

def fetch_avatar_url(endpoint_url, username):
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
    updated_rows = []
    user_found = False

    if file_exists:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    row['avatar_url'] = avatar_url
                    user_found = True
                updated_rows.append(row)

    if not user_found:
        updated_rows.append({'username': username, 'avatar_url': avatar_url})

    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['username', 'avatar_url'])
        writer.writeheader()
        writer.writerows(updated_rows)

    rankings_url = f"https://www.etoro.com/sapi/rankings/cid/{user_info['realCID']}/rankings/?Period=OneYearAgo"
    response = requests.get(rankings_url, headers=headers, proxies=proxy)
    response.raise_for_status()
    rankings_data = response.json()

    portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={user_info['realCID']}"
    response = requests.get(portfolio_url, headers=headers, proxies=proxy)
    response.raise_for_status()
    portfolio_data = response.json()

    return rankings_data['Data'], portfolio_data['AggregatedPositions'], avatar_url

def load_instrument_map():
    with open('C:/Users/aiden/OneDrive/Documents/Desktop/Stock Python Scripts/AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as file:
        instrument_map = json.load(file)
    return instrument_map

def map_portfolio_data(portfolio_data, instrument_map):
    mapped_portfolio_data = []
    for position in portfolio_data:
        instrument_id = position['InstrumentID']
        mapped_position = {
            'instrument_id': instrument_id,
            'ticker_name': instrument_map.get(str(instrument_id), 'Unknown'),
            'direction': position.get('Direction'),
            'invested': position.get('Invested'),
            'net_profit': position.get('NetProfit'),
            'value': position.get('Value')
        }
        mapped_portfolio_data.append(mapped_position)
    return mapped_portfolio_data

def fetch_etoro_data_for_user(username):
    # Implement the function to fetch eToro data for a user
    # This is a placeholder implementation
    endpoint_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
    rankings_data, portfolio_data, avatar_url = fetch_avatar_url(endpoint_url, username)
    return rankings_data, portfolio_data, avatar_url