import json
import requests

from datetime import datetime

def process_performance_data(data):
    performance = data.get('Data', {})
    
    # Load instrument_mapping.json
    with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
        instrument_mapping = json.load(f)

    # Convert TopTradedInstrumentId to ticker
    top_traded_instrument_id = performance.get('TopTradedInstrumentId', 'N/A')
    top_traded_instrument = instrument_mapping.get(str(top_traded_instrument_id), 'N/A')

    importance = {
        "Gain": 5,
        "Daily Gain": 4,
        "This Week Gain": 4,
        "Risk Score": 5,
        "Max Daily Risk Score": 4,
        "Max Monthly Risk Score": 4,
        "Copiers": 3,
        "Trades": 3,
        "Win Ratio": 4,
        "Daily Drawdown (DD)": 3,
        "Weekly Drawdown (DD)": 3,
        "Profitable Weeks Percentage": 4,
        "Profitable Months Percentage": 4,
        "Exposure": 4,
        "Average Position Size": 3,
        "Long Position Percentage": 3,
        "Max Experienced Drawdown": 4,
        "Drawdown Period": 3,
        "Top Traded Instrument": 3
    }

    def format_date(date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            return date_obj.strftime("%d-%m-%y")
        except ValueError:
            return date_str

    drawdown_start = format_date(performance.get('PeakToValleyStart', 'N/A'))
    drawdown_end = format_date(performance.get('PeakToValleyEnd', 'N/A'))

    relevant_metrics = {
        "Gain": {"value": f"{performance.get('Gain', 'N/A')}%", "importance": importance["Gain"]},
        "Daily Gain": {"value": f"{performance.get('DailyGain', 'N/A')}%", "importance": importance["Daily Gain"]},
        "This Week Gain": {"value": f"{performance.get('ThisWeekGain', 'N/A')}%", "importance": importance["This Week Gain"]},
        "Risk Score": {"value": performance.get('RiskScore', 'N/A'), "importance": importance["Risk Score"]},
        "Max Daily Risk Score": {"value": performance.get('MaxDailyRiskScore', 'N/A'), "importance": importance["Max Daily Risk Score"]},
        "Max Monthly Risk Score": {"value": performance.get('MaxMonthlyRiskScore', 'N/A'), "importance": importance["Max Monthly Risk Score"]},
        "Copiers": {"value": performance.get('Copiers', 'N/A'), "importance": importance["Copiers"]},
        "Trades": {"value": performance.get('Trades', 'N/A'), "importance": importance["Trades"]},
        "Win Ratio": {"value": f"{performance.get('WinRatio', 'N/A')}%", "importance": importance["Win Ratio"]},
        "Daily Drawdown (DD)": {"value": f"{performance.get('DailyDD', 'N/A')}%", "importance": importance["Daily Drawdown (DD)"]},
        "Weekly Drawdown (DD)": {"value": f"{performance.get('WeeklyDD', 'N/A')}%", "importance": importance["Weekly Drawdown (DD)"]},
        "Profitable Weeks Percentage": {"value": f"{performance.get('ProfitableWeeksPct', 'N/A')}%", "importance": importance["Profitable Weeks Percentage"]},
        "Profitable Months Percentage": {"value": f"{performance.get('ProfitableMonthsPct', 'N/A')}%", "importance": importance["Profitable Months Percentage"]},
        "Exposure": {"value": f"{performance.get('Exposure', 'N/A')}%", "importance": importance["Exposure"]},
        "Average Position Size": {"value": f"{performance.get('AvgPosSize', 'N/A')}%", "importance": importance["Average Position Size"]},
        "Long Position Percentage": {"value": f"{performance.get('LongPosPct', 'N/A')}%", "importance": importance["Long Position Percentage"]},
        "Max Experienced Drawdown": {"value": f"{performance.get('PeakToValley', 'N/A')}%", "importance": importance["Max Experienced Drawdown"]},
        "Drawdown Period": {"value": f"{drawdown_start} to {drawdown_end}", "importance": importance["Drawdown Period"]},
        "Top Traded Instrument": {"value": top_traded_instrument, "importance": importance["Top Traded Instrument"]}
    }
    return relevant_metrics

def fetch_user_performance():
    # Load cid_mapping.json
    with open('AutomatingEtoroPosts/mapping/cid_mapping.json', 'r') as f:
        cid_mapping = json.load(f)

    user_performance_data = {}

    # Loop through each cid_value in cid_mapping
    for username, cid_value in cid_mapping.items():
        url = f"https://www.etoro.com/sapi/rankings/cid/{cid_value}/rankings/?Period=LastTwoYears"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            performance = data.get('Data', {})

            # Process performance data
            user_performance_data[username] = process_performance_data(data)
            print(f"Fetched data for {username} (CID: {cid_value})")
        except requests.RequestException as e:
            print(f"Error fetching data for {username} (CID: {cid_value}): {e}")
            user_performance_data[username] = {"error": str(e)}

    # Write the output to user_performance_data.json
    with open('user_performance_data.json', 'w') as outfile:
        json.dump(user_performance_data, outfile, indent=4)
    print("User performance data has been written to user_performance_data.json")

if __name__ == "__main__":
    fetch_user_performance()