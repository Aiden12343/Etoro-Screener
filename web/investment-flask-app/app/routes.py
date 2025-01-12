from flask import render_template, request, current_app, redirect, url_for
import csv
from .metrics import fetch_user_data, load_instrument_map, map_instrument_ids
import matplotlib.pyplot as plt
from collections import defaultdict

instrument_map = load_instrument_map("investment-flask-app/AutomatingEtoroPosts/mapping/instrument_mapping.json")

# Route for the main landing page
@current_app.route('/')
def main():
    return render_template('main.html')

@current_app.route('/average')
def average():
    portfolio_file_path = 'investment-flask-app/AutomatingEtoroPosts/mapping/etoro_csv_contents/portfolio_data.csv'
    aggregated_data = defaultdict(lambda: {'long': 0, 'short': 0, 'total_pl': 0, 'total_value': 0, 'total_invested': 0, 'count': 0})
    usernames = set()
    with open(portfolio_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            instrument_id, ticker_name, direction, invested, net_profit, value, username = row
            invested   = float(invested)
            net_profit = float(net_profit)
            value      = float(value)
            usernames.add(username)
            if direction == 'Buy':
                aggregated_data[ticker_name]['long']      += 1
            else:
                aggregated_data[ticker_name]['short']      += 1
            aggregated_data[ticker_name]['total_pl']       += net_profit
            aggregated_data[ticker_name]['total_value']    += value
            aggregated_data[ticker_name]['total_invested'] += invested
            aggregated_data[ticker_name]['count']          += 1
    average_data = []
    for ticker_name, data in aggregated_data.items():
        long_short_ratio     = f"{data['long']}       :{data['short']}"
        average_pl           = data['total_pl']       / data['count']
        average_value_pct    = (data['total_value']   / data['total_invested']) * 100 if data['total_invested'] > 0 else 0
        average_invested_pct = data['total_invested'] / data['count']
        average_data.append({
            'ticker_name'         : ticker_name,
            'long_short_ratio'    : long_short_ratio,
            'total_long_short'    : data['long'] + data['short'], 
            'average_pl'          : round(average_pl, 2),
            'average_value_pct'   : round(average_value_pct, 2),
            'average_invested_pct': round(average_invested_pct, 2)
        })
    sort_by    = request.args.get('sort' , 'ticker_name')
    sort_order = request.args.get('order', 'asc')
    reverse    = (sort_order == 'desc')
    if sort_by == 'long_short_ratio':
        average_data.sort(key=lambda x: x['total_long_short'], reverse=reverse)
    else:
        average_data.sort(key=lambda x: x[sort_by], reverse=reverse)
    next_order     = 'desc' if sort_order == 'asc' else 'asc'
    username_count = len(usernames)

    return render_template('average.html', average_data=average_data, sort_by=sort_by, sort_order=sort_order, next_order=next_order, username_count=username_count)

@current_app.route('/ticker/<ticker_name>')
def ticker(ticker_name):
    portfolio_file_path = 'investment-flask-app/AutomatingEtoroPosts/mapping/etoro_csv_contents/portfolio_data.csv'
    ticker_data = []

    # Load portfolio data from CSV
    with open(portfolio_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            instrument_id, ticker, direction, invested, net_profit, value, username = row
            if ticker == ticker_name:
                ticker_data.append({
                    'username'     : username,
                    'instrument_id': instrument_id,
                    'ticker_name'  : ticker,
                    'direction'    : direction,
                    'invested'     : float(invested),
                    'net_profit'   : float(net_profit),
                    'value'        : float(value)
                })
    sort_by    = request.args.get('sort', 'username')
    sort_order = request.args.get('order', 'asc')
    reverse    = (sort_order == 'desc')
    ticker_data.sort(key=lambda x: x[sort_by], reverse=reverse)
    next_order = 'desc' if sort_order == 'asc' else 'asc'

    return render_template('ticker.html', ticker_name=ticker_name, ticker_data=ticker_data, sort_by=sort_by, sort_order=sort_order, next_order=next_order)

@current_app.route('/search', methods=['POST'])
def search_user():
    username = request.form['username']
    return redirect(url_for('user_portfolio', username=username))

@current_app.route('/user/<username>')
def user_performance(username):
    try:
        user_heatmap_data, portfolio_data, risk_exposure_data = fetch_user_data(username)
        mapped_portfolio_data                                 = map_instrument_ids(portfolio_data, instrument_map)
        mapped_risk_exposure_data                             = map_instrument_ids(risk_exposure_data, instrument_map)
        sort_by    = request.args.get('sort', 'InstrumentID')
        sort_order = request.args.get('order', 'asc')
        page       = int(request.args.get('page', 1))
        per_page = 5
        reverse  = (sort_order == 'desc')
        mapped_portfolio_data.sort(key=lambda x: x[sort_by], reverse=reverse)
        start          = (page - 1) * per_page
        end            = start + per_page
        paginated_data = mapped_portfolio_data[start:end]
        has_more_data  = len(mapped_portfolio_data) > end
        next_order     = 'desc' if sort_order == 'asc' else 'asc'

        return render_template('username.html', username=username, portfolio_data=paginated_data, user_heatmap_data=user_heatmap_data, risk_exposure_data=mapped_risk_exposure_data, sort_by=sort_by, sort_order=sort_order, next_order=next_order, page=page, has_more_data=has_more_data)
    except Exception as e:
        return f"An error occurred: {e}", 500
