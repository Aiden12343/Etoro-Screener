import sys
import json
import csv
import requests
import os

# --- Load Instrument Map ---
def load_instrument_map():
    try:
        with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
            instrument_map = json.load(f)
    except FileNotFoundError:
        instrument_map = {}
    return instrument_map

# --- Add JSON Data to Portfolio CSV ---
def add_json_to_csv(json_data, csv_file_path, instrument_map):
    try:
        with open(csv_file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for username, portfolio_data in json_data.items():
                for position in portfolio_data:
                    instrument_id = position.get("InstrumentID", "N/A")
                    ticker_name = instrument_map.get(str(instrument_id), "Unknown Ticker")
                    writer.writerow([instrument_id, ticker_name, position.get("Direction", "N/A"),
                                     position.get("Invested", "N/A"), position.get("NetProfit", "N/A"),
                                     position.get("Value", "N/A"), username])
        print("Successfully updated CSV data.")
    except Exception as e:
        print(f"Error adding/updating CSV: {e}")

# --- Load CID Mapping ---
def load_cid_mapping(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    return {}

# --- Save CID Mapping ---
def save_cid_mapping(filepath, cid_mapping):
    with open(filepath, 'w') as file:
        json.dump(cid_mapping, file, indent=4)

# --- Append to CSV ---
def append_to_csv(filepath, row):
    file_exists = os.path.isfile(filepath)
    with open(filepath, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Username'])  # Write header if file is new
        writer.writerow(row)

# --- Hardcoded Proxies ---
def load_proxies():
    return [
        "130.162.180.254:8888",
        "101.255.166.242:8080",
        "13.80.134.180:80",
        "133.18.234.13:80",
        "101.32.14.101:1080"
    ]

# --- Fetch Etoro Data for User ---
def fetch_etoro_data_for_user(username, instrument_map, proxies):
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

    for proxy in proxies:
        session = requests.Session()
        session.headers.update(headers)
        session.proxies.update({
            'http': proxy,
            'https': proxy,
        })

        try:
            user_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
            response = session.get(user_url)
            if response.status_code == 404:
                print(f"Error: Username {username} does not exist on eToro.")
                return
            elif response.status_code != 200:
                print(f"Error: Unable to fetch data for {username}, HTTP Status Code: {response.status_code}")
                continue

            user_data = response.json()
            realCID = user_data.get("realCID")
            gcid = user_data.get("gcid")
            demoCID = user_data.get("demoCID")

            if not realCID or not gcid or not demoCID:
                print(f"Error: Missing data for {username}")
                return

            # Update cid_mapping.json
            cid_mapping_filepath = 'AutomatingEtoroPosts/etoro_csv_contents/cid_mapping.json'
            cid_mapping = load_cid_mapping(cid_mapping_filepath)
            cid_mapping[username] = realCID
            save_cid_mapping(cid_mapping_filepath, cid_mapping)

            # Update username.csv
            username_csv_filepath = 'AutomatingEtoroPosts/etoro_csv_contents/username.csv'
            append_to_csv(username_csv_filepath, [username])

            portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={realCID}"
            portfolio_response = session.get(portfolio_url)
            if portfolio_response.status_code != 200:
                print(f"Error fetching portfolio data for {username}: HTTP Status Code: {portfolio_response.status_code}")
                continue

            portfolio_data = portfolio_response.text
            portfolio_data_json = json.loads(portfolio_data)

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

            add_json_to_csv({username: user_portfolio}, 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', instrument_map)
            break  # Exit loop if successful
        except Exception as e:
            print(f"Error with proxy {proxy}: {e}")

# --- Get CID for Username ---
def get_cid_for_username(username):
    with open('AutomatingEtoroPosts/mapping/cid_mapping.json', 'r') as f:
        cid_mapping = json.load(f)
    return cid_mapping.get(username)

# --- Fetch Performance Data ---
def fetch_performance_data(cid):
    url = f"https://www.etoro.com/sapi/rankings/cid/{cid}/rankings/?Period=OneYearAgo"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# --- Main Function ---
def main(username):
    cid = get_cid_for_username(username)
    if not cid:
        print(json.dumps({"error": f"CID for username {username} not found."}))
        return

    performance_data = fetch_performance_data(cid)
    if not performance_data:
        print(json.dumps({"error": f"Performance data for CID {cid} not found."}))
        return

    print(json.dumps(performance_data, indent=4))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python merged_script.py <username>"}))
    else:
        username = sys.argv[1]
        instrument_map = load_instrument_map()
        proxies = load_proxies()
        fetch_etoro_data_for_user(username, instrument_map, proxies)
        main(username)

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