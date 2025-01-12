import json
import requests

def get_proxies():
    return {}

def get_headers():
    return {
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

def fetch_user_data(username):
    headers = get_headers() 
    proxies = get_proxies()

    print("Fetching user data for: https://www.etoro.com/api/logininfo/v1.1/users/{username}")
    endpoint_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
    response = requests.get(endpoint_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    cid_data = response.json() 
    avatar_url = next((avatar['url'] for avatar in cid_data['avatars'] if avatar['type'] == 'Original'), None)
    about_me   = cid_data['aboutMeShort']


    print("Fetching risk score data and rankings for : https://www.etoro.com/sapi/rankings/cid/{cid_data['realCID']}/rankings/?Period=OneYearAgo")
    rankings_url = f"https://www.etoro.com/sapi/rankings/cid/{cid_data['realCID']}/rankings/?Period=OneYearAgo"
    response = requests.get(rankings_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    rankings_data = response.json()

    print("Fetching portfolio data for https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={cid_data['realCID']}")
    portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={cid_data['realCID']}"
    response = requests.get(portfolio_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    portfolio_data = response.json()

    print("Fetching risk score contribution data for https://www.etoro.com/sapi/userstats/risk/UserName/{username}/Contribution")
    risk_exposure_url = f"https://www.etoro.com/sapi/userstats/risk/UserName/{username}/Contribution"
    response = requests.get(risk_exposure_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    risk_exposure_data = response.json()

    return rankings_data['Data'], portfolio_data['AggregatedPositions'], risk_exposure_data, avatar_url, about_me

def load_instrument_map(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
    
def map_instrument_ids(data, instrument_map):
    for item in data:
        instrument_id = None
        for key in item:
            if key.lower() == 'instrumentid':
                instrument_id = item.get(key)
                break
        if instrument_id is not None:
            instrument_id = str(instrument_id).lower()
            if instrument_id in instrument_map:
                item['TickerName'] = instrument_map[instrument_id]
            else:
                print(f"InstrumentID {instrument_id} not found in instrument_map.")
                item['TickerName'] = 'Unknown'
        else:
            item['TickerName'] = 'Unknown'
    return data