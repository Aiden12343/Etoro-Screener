# Etoro-Screener
Summary -
This repo allows the following functions --->

# 1.
----> effective real-time tracking of etoro-portfolios through the use of Chromium webdrivers
----> ability to collate portfolio data to generate statistical analysis, average positions, most common positions, long to short ratios, and plot the change in shareholder ownership.
----> ability to locate the liquidation levels of specific users as well as average liquidation levels across the whole set of users.
----> identify in real-time what trades are the most popular, and which are performing the best, worst and which are not garnerning much attention.

# Files used @ 1
----> @reading_portfolios.py to use a Chromium webdriver to load URL's and interact with GUI
----> @etoro_usernames.csv to store a set of usernames for the reading_portfolios.py
----> @etoro_portfolios.py to launch a locally hosted site containing the data collated
----> @portfolio_cleaned.csv to store a the resulting portfolio data in format { Ticker,Ticker_Long_Form,Direction,Exposure (%),P/L (%),Total Value (%),Username }

# 2. 
----> Ability to automate trades through the use of Chromium webdrivers
----> Ability to log trades made, storing timestampes, dollar values and ticker ID's
----> Ability to add custom boolean logic for making new trades
----> Ability to loop system to check for new buy signals every x interval
----> Supports ability to choose between Virtual and Real accounts
----> Supports ability to define your own $ amounts for a purchase
----> Ability to detect if a stock is not listed on etoro, and will skip the stock without issue.

# Files used @ 2
----> @automate_trade.py to use a Chromium webdriver to load URL's and interact with GUI
----> @automate.tickers.csv to store a CSV file of all the tickers we wish to check for trade signals
----> @error_log.txt to store any errors that may occur during script run (errors are suppressed from terminal output)
----> @trade_log.txt to store all trades, with timestamps and $ amounts.

# Additional Notes
It is not advised for one to load more than 40 tickers/usernames at any given time, as eToro will detect and likely sign you out or force-crash to block your automated process.

There is currently a bug with --headless flags in both scripts, where the JS tags are not identified when running in --headless. 
 The workaround is to use pyautogui to load the browser in another virtual destop for windows, and then switch back to the main whilst it processes.

# Future updates

----> Support for tracking Stop Losses of specific assets
----> Support for filtering by leveraged assets only
----> Support for tracking historical closed positions
----> Plotting active and historical positions of average portfolios for different assets against the relevant chart.
----> Ability to reverse a specific users portfolio, link to an automated trading system which trades the inverse.
