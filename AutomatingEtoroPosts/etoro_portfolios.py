import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# --- Flask Route to Render Portfolio Table Summary (Merged) ---
@app.route("/")
def portfolio_summary():
    try:
        # Load the CSV into a pandas DataFrame
        df = pd.read_csv("AutomatingEtoroPosts/portfolio_cleaned.csv")
        
        # Group by Ticker and calculate average values for P/L, Exposure, and Total Value
        summary_df = df.groupby("Ticker").agg(
            {
                "Exposure (%)": "mean",
                "P/L (%)": "mean",
                "Total Value (%)": "mean",
                "Direction": lambda x: f"{(x == 'Long').sum()} Long : {(x == 'Short').sum()} Short"
            }
        ).reset_index()

        # Convert the summary DataFrame to an HTML table with Bootstrap classes
        data_html = summary_df.to_html(classes="table table-striped table-dark", index=False)
        
        # Pass the HTML table to the template
        return render_template("portfolio_summary.html", data=data_html)
    
    except FileNotFoundError:
        return render_template("portfolio_summary.html", data=None)

# --- Flask Route to Render Specific User's Portfolio ---
@app.route("/<username>")
def user_portfolio(username):
    try:
        # Load the CSV into a pandas DataFrame
        df = pd.read_csv("AutomatingEtoroPosts/portfolio_cleaned.csv")
        
        # Filter the data for the specific user
        user_df = df[df["Username"] == username]
        
        # Convert the user portfolio DataFrame to an HTML table with Bootstrap classes
        data_html = user_df.to_html(classes="table table-striped table-dark", index=False)
        
        # Pass the HTML table to the template
        return render_template("user_portfolio.html", username=username, data=data_html)
    
    except FileNotFoundError:
        return render_template("user_portfolio.html", username=username, data=None)

if __name__ == "__main__":
    app.run(debug=True)
