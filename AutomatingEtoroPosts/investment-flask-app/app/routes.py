import requests
from flask import render_template, request, current_app
import csv
from AutomatingEtoroPosts.metrics import load_instrument_map, fetch_etoro_data_for_user, map_portfolio_data
from collections import defaultdict
import json
import os
from .fetch_avatar import fetch_avatar_url  # Import the fetch_avatar_url function

# Load instrument map
instrument_map = load_instrument_map()

# Route for the main landing page
@current_app.route('/')
def main():
    return render_template('main.html')

# Route for the averaged portfolio contents
@current_app.route('/average')
def average():
    portfolio_file_path = 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv'
    aggregated_data = defaultdict(lambda: {'long': 0, 'short': 0, 'total_pl': 0, 'total_value': 0, 'total_invested': 0, 'count': 0})
    usernames = set()

    # Load portfolio data from CSV
    with open(portfolio_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            instrument_id, ticker_name, direction, invested, net_profit, value, username = row
            invested = float(invested)
            net_profit = float(net_profit)
            value = float(value)
            usernames.add(username)

            if direction == 'Buy':
                aggregated_data[ticker_name]['long'] += 1
            else:
                aggregated_data[ticker_name]['short'] += 1

            aggregated_data[ticker_name]['total_pl'] += net_profit
            aggregated_data[ticker_name]['total_value'] += value
            aggregated_data[ticker_name]['total_invested'] += invested
            aggregated_data[ticker_name]['count'] += 1

    # Calculate averages and ratios
    average_data = []
    for ticker_name, data in aggregated_data.items():
        long_short_ratio = f"{data['long']}:{data['short']}"
        average_pl = data['total_pl'] / data['count']
        average_value_pct = (data['total_value'] / data['total_invested']) * 100 if data['total_invested'] > 0 else 0
        average_invested_pct = data['total_invested'] / data['count']

        average_data.append({
            'ticker_name': ticker_name,
            'long_short_ratio': long_short_ratio,
            'total_long_short': data['long'] + data['short'],  # Add total long + short for sorting
            'average_pl': round(average_pl, 2),
            'average_value_pct': round(average_value_pct, 2),
            'average_invested_pct': round(average_invested_pct, 2)
        })

    # Get sorting parameters from request
    sort_by = request.args.get('sort', 'ticker_name')
    sort_order = request.args.get('order', 'asc')

    # Sort the data
    reverse = (sort_order == 'desc')
    if sort_by == 'long_short_ratio':
        average_data.sort(key=lambda x: x['total_long_short'], reverse=reverse)
    else:
        average_data.sort(key=lambda x: x[sort_by], reverse=reverse)

    # Toggle sort order for next click
    next_order = 'desc' if sort_order == 'asc' else 'asc'

    # Count the number of unique usernames
    username_count = len(usernames)

    return render_template('average.html', average_data=average_data, sort_by=sort_by, sort_order=sort_order, next_order=next_order, username_count=username_count)

# Route for detailed ticker breakdown
@current_app.route('/ticker/<ticker_name>')
def ticker(ticker_name):
    portfolio_file_path = 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv'
    ticker_data = []

    # Load portfolio data from CSV
    with open(portfolio_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            instrument_id, ticker, direction, invested, net_profit, value, username = row
            if ticker == ticker_name:
                ticker_data.append({
                    'username': username,
                    'instrument_id': instrument_id,
                    'ticker_name': ticker,
                    'direction': direction,
                    'invested': float(invested),
                    'net_profit': float(net_profit),
                    'value': float(value)
                })

    # Get sorting parameters from request
    sort_by = request.args.get('sort', 'username')
    sort_order = request.args.get('order', 'asc')

    # Sort the data
    reverse = (sort_order == 'desc')
    ticker_data.sort(key=lambda x: x[sort_by], reverse=reverse)

    # Toggle sort order for next click
    next_order = 'desc' if sort_order == 'asc' else 'asc'

    return render_template('ticker.html', ticker_name=ticker_name, ticker_data=ticker_data, sort_by=sort_by, sort_order=sort_order, next_order=next_order)

# Load instrument map
instrument_map = load_instrument_map()

@current_app.route('/user/<username>')
def user_performance(username):
    try:
        # Fetch user data from the APIs using proxies and headers
        user_heatmap_data, portfolio_data, _ = fetch_etoro_data_for_user(username)

        # Fetch avatar URL using fetch_avatar_url function
        avatar_url = fetch_avatar_url(f"https://www.etoro.com/api/logininfo/v1.1/users/{username}", username)
        user_heatmap_data['avatar_url'] = avatar_url

        # Debugging statement
        print(f"Avatar URL added to user_heatmap_data: {user_heatmap_data['avatar_url']}")

        # Map portfolio data with instrument map
        mapped_portfolio_data = map_portfolio_data(portfolio_data, instrument_map)

        # Fetch risk exposure data
        risk_exposure_url = f"https://www.etoro.com/sapi/userstats/risk/UserName/{username}/Contribution"
        response = requests.get(risk_exposure_url)
        response.raise_for_status()
        risk_exposure_data = response.json()

        # Map instrumentId to ticker names
        for item in risk_exposure_data:
            item['ticker_name'] = instrument_map.get(str(item['instrumentId']), 'Unknown')

        # Get sorting parameters from request
        sort_by = request.args.get('sort', 'instrument_id')
        sort_order = request.args.get('order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = 10

        # Sort the data
        reverse = (sort_order == 'desc')
        mapped_portfolio_data.sort(key=lambda x: x[sort_by], reverse=reverse)

        # Paginate the data
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = mapped_portfolio_data[start:end]

        # Check if there is more data for the next page
        has_more_data = len(mapped_portfolio_data) > end

        # Toggle sort order for next click
        next_order = 'desc' if sort_order == 'asc' else 'asc'

        return render_template('username.html', username=username, portfolio_data=paginated_data, user_heatmap_data=user_heatmap_data, risk_exposure_data=risk_exposure_data, sort_by=sort_by, sort_order=sort_order, next_order=next_order, page=page, has_more_data=has_more_data)
    except Exception as e:
        return f"An error occurred: {e}", 500

# Route to clear temporary JSON files when a new user is searched for
@current_app.route('/clear_temp_files')
def clear_temp_files():
    for file in os.listdir('.'):
        if file.startswith('temp_') and file.endswith('.json'):
            os.remove(file)
    return "Temporary files cleared", 200