import csv
import json
import os
import requests

#---- Proxies and Headers ----#
def get_proxies():
    # Define your proxy settings here
    return {
    }

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
    proxies = get_proxies()  # Define your proxies

    # Get realcid
    print("Fetching user data for:", username)
    endpoint_url = f"https://www.etoro.com/api/logininfo/v1.1/users/{username}"
    response = requests.get(endpoint_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    cid_data = response.json() 
    real_cid = cid_data['realCID']
    print(real_cid)   
    
    # Risk score data and rankings
    print("Fetching risk score data and rankings")
    rankings_url = f"https://www.etoro.com/sapi/rankings/cid/{cid_data['realCID']}/rankings/?Period=OneYearAgo"
    response = requests.get(rankings_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    rankings_data = response.json()

    # Portfolio data
    print("Fetching portfolio data")
    portfolio_url = f"https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid={cid_data['realCID']}"
    response = requests.get(portfolio_url, headers=headers, proxies=proxies)
    response.raise_for_status()
    portfolio_data = response.json()
    print(portfolio_data)

    return rankings_data['Data'], portfolio_data['AggregatedPositions'], real_cid

def load_instrument_map(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
    
def map_instrument_ids(aggregated_positions, instrument_map):
    for position in aggregated_positions:
        instrument_id = str(position['InstrumentID'])
        position['TickerName'] = instrument_map.get(instrument_id, 'Unknown')
    return aggregated_positions


def fetch_risk_score_data(real_cid, username):
    headers = get_headers()
    proxies = get_proxies()
    payload = {
    "groups": [
        {
            "groupId": 0,
            "dataComponents": [{"type": "Performance"}],
            "minRequiredItems": 2,
            "isMandatory": True,
        },
        {
            "groupId": 1,
            "dataComponents": [
                {"type": "PortfolioRisk"},
                {
                    "type": "ExpectedDividends",
                    "params": {
                        "totalAmount": 0,
                        "assetsPercentages": {
                        },
                    },
                },
                {"type": "TradingStats"},
                {"type": "AdditionalStats"},
            ],
            "minRequiredItems": 1,
            "isMandatory": True,
        },
        {
            "groupId": 2,
            "dataComponents": [
                {
                    "type": "ComparePortfolio",
                    "params": {
                        "itemsToCompare": [
                        ]
                    },
                },
                {"type": "CopiersStats"},
            ],
            "minRequiredItems": 2,
            "isMandatory": True,
        },
    ]
}
    print("Fetching risk score data")
    risk_score_url = f"https://www.etoro.com/api/userpagestats/v1/user/{real_cid}/stats/components"
    response = requests.post(risk_score_url, headers=headers, proxies=proxies, json=payload)
    response.raise_for_status()
    risk_score_data = response.json()
    
    with open("testoutput.json", "w") as file:
        if response.status_code == 200:
            json.dump(risk_score_data, file, indent=1)
        else:
            file.write(f"Error: Received status code {response.status_code}\n")
            file.write(response.text)
    
    # Debug print to check the structure of the JSON response
    print(json.dumps(risk_score_data, indent=4))
    
    # Extract the specific set of data with error handling
    try:
        portfolio_risk_data = None
        for component in risk_score_data.get("dataComponentsResponse", []):
            if component.get("type") == "PortfolioRisk":
                component_data = component.get("componentData", {})
                portfolio_risk_data = {
                    "type": component.get("type"),
                    "componentData": {
                        "averageRiskScore": component_data.get("averageRiskScore"),
                        "dailyDrawdown": component_data.get("dailyDrawdown"),
                        "weeklyDrawdown": component_data.get("weeklyDrawdown"),
                        "peakToValleyDrawdown": component_data.get("peakToValleyDrawdown"),
                    }
                }
                break
        if portfolio_risk_data is None:
            print("Error: 'PortfolioRisk' data not found in the response")
    except (KeyError, AttributeError) as e:
        print(f"Error: {e}")
        portfolio_risk_data = None
    
    return portfolio_risk_data