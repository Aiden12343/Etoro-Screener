# Etoro-Screener
Summary -<br>
This repo allows the following functions ---><br>

# 1.
----> effective real-time tracking of etoro-portfolios through the use of Chromium webdrivers <br>
----> ability to collate portfolio data to generate statistical analysis, average positions, most common positions, long to short ratios, and plot the change in shareholder ownership.<br>
----> ability to locate the liquidation levels of specific users as well as average liquidation levels across the whole set of users.<br>
----> identify in real-time what trades are the most popular, and which are performing the best, worst and which are not garnerning much attention.<br>

# Files used @ 1
----> @reading_portfolios.py to use a Chromium webdriver to load URL's and interact with GUI<br>
----> @etoro_usernames.csv to store a set of usernames for the reading_portfolios.py<br>
----> @etoro_portfolios.py to launch a locally hosted site containing the data collated<br>
----> @portfolio_cleaned.csv to store a the resulting portfolio data in format { Ticker,Ticker_Long_Form,Direction,Exposure (%),P/L (%),Total Value (%),Username }<br>

# 2. 
----> Ability to automate trades through the use of Chromium webdrivers<br>
----> Ability to log trades made, storing timestampes, dollar values and ticker ID's<br>
----> Ability to add custom boolean logic for making new trades<br>
----> Ability to loop system to check for new buy signals every x interval<br>
----> Supports ability to choose between Virtual and Real accounts<br>
----> Supports ability to define your own $ amounts for a purchase<br>
----> Ability to detect if a stock is not listed on etoro, and will skip the stock without issue.<br>

# Files used @ 2
----> @automate_trade.py to use a Chromium webdriver to load URL's and interact with GUI<br>
----> @automate.tickers.csv to store a CSV file of all the tickers we wish to check for trade signals<br>
----> @error_log.txt to store any errors that may occur during script run (errors are suppressed from terminal output)<br>
----> @trade_log.txt to store all trades, with timestamps and $ amounts.<br>

# Additional Notes
It is not advised for one to load more than 40 tickers/usernames at any given time, as eToro will detect and likely sign you out or force-crash to block your automated process.<br>

There is currently a bug with --headless flags in both scripts, where the JS tags are not identified when running in --headless. <br>
The workaround is to use pyautogui to load the browser in another virtual destop for windows, and then switch back to the main whilst it processes.<br>

# Future updates

----> Support for tracking Stop Losses of specific assets<br>
----> Support for filtering by leveraged assets only<br>
----> Support for tracking historical closed positions<br>
----> Plotting active and historical positions of average portfolios for different assets against the relevant chart.<br>
----> Ability to reverse a specific users portfolio, link to an automated trading system which trades the inverse.<br>
