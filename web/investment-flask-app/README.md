# Investment Flask App

## Overview
The Investment Flask App is a web application designed to provide users with insights into their investment portfolios. It features a clean and user-friendly interface that allows users to view averaged portfolio contents, detailed ticker breakdowns, and individual user performance metrics.

## Project Structure
```
investment-flask-app
├── app
│   ├── __init__.py
│   ├── routes.py
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   └── js
│   │       └── scripts.js
│   └── templates
│       ├── layout.html
│       ├── main.html
│       ├── average.html
│       ├── ticker.html
│       └── username.html
├── AutomatingEtoroPosts
│   ├── mapping
│   │   └── instrument_mapping.json
│   └── metrics.py
├── requirements.txt
├── run.py
└── README.md
```

## Features
- **Main Landing Page**: An overview of the application with links to other sections.
- **Averaged Portfolio Contents**: Displays a table of averaged portfolio data with sorting capabilities.
- **Detailed Ticker Breakdown**: Provides insights into specific tickers, including filtering and sorting options.
- **User-Specific Performance Page**: Shows performance metrics for individual users in a heatmap format.

## Setup Instructions
1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd investment-flask-app
   ```

2. **Install Dependencies**:
   Ensure you have Python and pip installed. Then run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   Execute the following command to start the Flask development server:
   ```
   python run.py
   ```

4. **Access the Application**:
   Open your web browser and navigate to `http://127.0.0.1:5000` to view the application.

## Dependencies
- Flask
- Any other necessary libraries listed in `requirements.txt`.

## License
This project is licensed under the MIT License - see the LICENSE file for details.