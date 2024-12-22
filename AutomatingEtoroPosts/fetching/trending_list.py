import requests
import csv
import json
from collections import Counter

# URL to fetch trending list data
url = "https://www.etoro.com/sapi/rankings/rankings/?blocked=false&bonusonly=false&copiedtradesmax=0&copiedtradesmin=0&copiersmax=700&copyblock=false&copyinvestmentpctmax=0&copyinvestmentpctmin=0&copytradespctmax=0&copytradespctmin=0&dailyddmin=-5&displayfullname=true&gainmax=55&gainmin=0&hasavatar=true&isfund=false&istestaccount=false&maxdailyriskscoremax=7&maxmonthlyriskscoremax=7&optin=true&page=1&pagesize=100&peaktovalleymin=-15&period=LastTwoYears&popularinvestor=true&sort=-gain&toptradedassetclassid=5&verified=true&weeklyddmin=-10"

# Fetch data from the URL
response = requests.get(url)
data = response.json()

# Check if the response status is OK
if data["Status"] != "OK":
    print("Failed to fetch data")
    exit()

# Extract items from the response
items = data["Items"]

# Define the CSV file paths
csv_file_path = "AutomatingEtoroPosts/etoro_csv_contents/etoro_trending_list.csv"
usernames_file_path = "AutomatingEtoroPosts/etoro_csv_contents/etoro_usernames.csv"
cid_mapping_file_path = "AutomatingEtoroPosts/mapping/cid_mapping.json"

# Define the CSV headers
headers = [
    "CustomerId", "UserName", "FullName", "HasAvatar", "IsSocialConnected", "IsTestAccount",
    "DisplayFullName", "BonusOnly", "Blocked", "Verified", "PopularInvestor", "CopyBlock",
    "IsFund", "IsBronze", "FundType", "Tags", "Gain", "DailyGain", "ThisWeekGain", "RiskScore",
    "MaxDailyRiskScore", "MaxMonthlyRiskScore", "Copiers", "CopiedTrades", "CopyTradesPct",
    "CopyInvestmentPct", "BaseLineCopiers", "CopiersGain", "AUMTier", "AUMTierV2", "AUMTierDesc",
    "VirtualCopiers", "Trades", "WinRatio", "DailyDD", "WeeklyDD", "ProfitableWeeksPct",
    "ProfitableMonthsPct", "Velocity", "Exposure", "AvgPosSize", "OptimalCopyPosSize",
    "HighLeveragePct", "MediumLeveragePct", "LowLeveragePct", "PeakToValley", "PeakToValleyStart",
    "PeakToValleyEnd", "LongPosPct", "TopTradedInstrumentId", "TopTradedAssetClassId",
    "TopTradedInstrumentPct", "TotalTradedInstruments", "ActiveWeeks", "FirstActivity",
    "LastActivity", "ActiveWeeksPct", "WeeksSinceRegistration", "Country", "AffiliateId",
    "InstrumentPct"
]

# Write data to CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    for item in items:
        writer.writerow(item)

print(f"Data successfully written to {csv_file_path}")

# Load instrument mapping
with open('AutomatingEtoroPosts/mapping/instrument_mapping.json', 'r') as f:
    instrument_mapping = json.load(f)

# Load existing usernames
try:
    with open(usernames_file_path, 'r', newline='', encoding='utf-8') as f:
        existing_usernames = {line.strip() for line in f}
except FileNotFoundError:
    existing_usernames = set()

# Load existing cid_mapping
try:
    with open(cid_mapping_file_path, 'r') as f:
        cid_mapping = json.load(f)
except FileNotFoundError:
    cid_mapping = {}

# Calculate top 5 most popular traded assets
instrument_counter = Counter()
total_risk_score = 0
total_gain = 0
country_counter = Counter()
copiers_counter = Counter()
win_ratio_counter = Counter()

new_usernames = set()

for item in items:
    top_traded_instrument_id = str(item["TopTradedInstrumentId"])
    risk_score = item["RiskScore"]
    gain = item["Gain"]
    country = item["Country"]
    copiers = item["Copiers"]
    win_ratio = item["WinRatio"]
    username = item["UserName"]
    customer_id = item["CustomerId"]

    total_risk_score += risk_score
    total_gain += gain
    country_counter[country] += 1
    copiers_counter[username] = copiers
    win_ratio_counter[username] = win_ratio

    if top_traded_instrument_id in instrument_mapping:
        ticker = instrument_mapping[top_traded_instrument_id]
        instrument_counter[ticker] += 1

    # Add username to new_usernames if not already present
    if username not in existing_usernames:
        new_usernames.add(username)

    # Add customer_id to cid_mapping if not already present
    if str(customer_id) not in cid_mapping:
        cid_mapping[str(customer_id)] = {"realCID": customer_id}

# Get the top 5 most popular traded assets
top_5_traded_assets = instrument_counter.most_common(5)

# Calculate the average risk score
average_risk_score = total_risk_score / len(items)

# Calculate the average gain
average_gain = total_gain / len(items)

# Get the top 5 countries by number of popular investors
top_5_countries = country_counter.most_common(5)

# Get the top 5 investors by number of copiers
top_5_copiers = copiers_counter.most_common(5)

# Get the top 5 investors by win ratio
top_5_win_ratio = win_ratio_counter.most_common(5)

# Print the results
print("Top 5 Most Popular Traded Assets:")
for ticker, count in top_5_traded_assets:
    print(f"{ticker}: {count} times")

print(f"Average Risk Score: {average_risk_score:.2f}")
print(f"Average Gain: {average_gain:.2f}%")

print("Top 5 Countries by Number of Popular Investors:")
for country, count in top_5_countries:
    print(f"{country}: {count} investors")

print("Top 5 Investors by Number of Copiers:")
for username, copiers in top_5_copiers:
    print(f"{username}: {copiers} copiers")

print("Top 5 Investors by Win Ratio:")
for username, win_ratio in top_5_win_ratio:
    print(f"{username}: {win_ratio}% win ratio")

# Append new usernames to etoro_usernames.csv
with open(usernames_file_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for username in new_usernames:
        writer.writerow([username])

# Save updated cid_mapping.json
with open(cid_mapping_file_path, 'w') as f:
    json.dump(cid_mapping, f, indent=4)

print(f"New usernames added to {usernames_file_path}")
print(f"cid_mapping.json updated")