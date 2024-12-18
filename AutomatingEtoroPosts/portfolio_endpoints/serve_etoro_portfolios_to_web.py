from flask import Flask, render_template, request
import pandas as pd
import subprocess
import json
import csv
import time

app = Flask(__name__)

def fetch_user_data(username):
    try:
        # Run the Selenium script to fetch data for the specific user
        subprocess.run(['python', 'AutomatingEtoroPosts/portfolio_endpoints/fetch_data_script.py', username], check=True)
        
        # Wait for the script to finish and file to be written
        time.sleep(2)  # Adjust based on how long the script takes to execute
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while fetching data for {username}: {e}")
        return None
    
    # After running the script, read the CSV file and prepare data for rendering
    data = []
    try:
        with open('AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Assuming column names are consistent in the CSV file
                if row['Username'] == username:
                    data.append(row)
    except Exception as e:
        print(f"Error reading CSV for {username}: {e}")
        return None
    
    return data



@app.route("/search_user", methods=["GET", "POST"])
def search_user():
    username = request.form.get('username', '').strip()
    if username:
        user_data = fetch_user_data(username)
        
        # Using index-based column references for the user data (assuming we read CSV with index columns)
        if user_data:
            # Convert to list of dictionaries with indexed column references
            indexed_data = [
                {
                    0: row['InstrumentID'],   # Index 0: InstrumentID
                    1: row['Ticker'],         # Index 1: Ticker
                    2: row['Direction'],      # Index 2: Direction
                    3: row['Invested'],       # Index 3: Invested
                    4: row['NetProfit'],      # Index 4: NetProfit
                    5: row['Value'],          # Index 5: Value
                    6: row['Username']        # Index 6: Username
                } for row in user_data
            ]
            return render_template('user_data_table.html', user_data=indexed_data, username=username)
        else:
            return f"Error fetching data for {username}, please try again."
    return render_template('search_user.html')

#average portfolio
@app.route('/')
def index():
    # Read the CSV file
    csv_file = 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv'
    df = pd.read_csv(csv_file, header=None, names=['Username', 'Ticker', 'Direction', 'Invested', 'NetProfit', 'Value', 'Other'])

    # Remove unnecessary columns
    df = df[['Ticker', 'Direction', 'Invested', 'NetProfit', 'Value']]

    # Group by Ticker and calculate required aggregates
    grouped = df.groupby('Ticker').agg(
        Long=('Direction', lambda x: (x == 'Buy').sum()),
        Short=('Direction', lambda x: (x == 'Sell').sum()),
        AvgInvested=('Invested', 'mean'),
        AvgNetProfit=('NetProfit', 'mean'),
        AvgValue=('Value', 'mean')
    ).reset_index()

    # Calculate the Long:Short ratio
    grouped['Direction'] = grouped.apply(
        lambda row: f"{row['Long']} Long : {row['Short']} Short", axis=1
    )

    # Round and format percentage columns
    grouped['AvgInvested'] = grouped['AvgInvested'].apply(lambda x: f"{x:.2f}%")
    grouped['AvgNetProfit'] = grouped['AvgNetProfit'].apply(lambda x: f"{x:.2f}%")
    grouped['AvgValue'] = grouped['AvgValue'].apply(lambda x: f"{x:.2f}%")

    # Add CSS class for positive/negative values
    grouped['InvestedClass'] = grouped['AvgInvested'].apply(lambda x: 'positive' if not x.startswith('-') else 'negative')
    grouped['NetProfitClass'] = grouped['AvgNetProfit'].apply(lambda x: 'positive' if not x.startswith('-') else 'negative')
    grouped['ValueClass'] = grouped['AvgValue'].apply(lambda x: 'positive' if not x.startswith('-') else 'negative')

    # Remove Long and Short columns
    grouped = grouped[['Ticker', 'Direction', 'AvgInvested', 'AvgNetProfit', 'AvgValue', 'InvestedClass', 'NetProfitClass', 'ValueClass']]

    # Convert the DataFrame to a list of dictionaries for the template
    portfolio_data = grouped.to_dict(orient='records')

    return render_template('average_portfolio.html', data=portfolio_data)


if __name__ == '__main__':
    app.run(debug=True)

