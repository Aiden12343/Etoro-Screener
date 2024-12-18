import csv
import json

# Load the instrument ID to SymbolFull mapping from JSON file
def load_mapping():
    with open("AutomatingEtoroPosts/mapping/instrument_mapping.json", "r") as file:
        data = json.load(file)

        # Ensure data is a dictionary
        if not isinstance(data, dict):
            raise ValueError("The JSON data is not in the expected dictionary format.")

    return data

# Update the Ticker column in the portfolio CSV based on InstrumentID
def update_tickers_in_csv():
    # Load the mapping
    instrument_mapping = load_mapping()

    input_csv = "AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv"
    output_csv = "AutomatingEtoroPosts/etoro_csv_contents/portfolio_data_updated.csv"

    # Read the input CSV and modify the Ticker column
    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Loop through each row, replace the Ticker based on InstrumentID
        for row in reader:
            instrument_id = row['InstrumentID']  # Keep the InstrumentID as string to match the JSON keys
            # Check if the InstrumentID exists in the mapping
            if instrument_id in instrument_mapping:
                # Replace the Ticker with the mapped SymbolFull (new ticker)
                row['Ticker'] = instrument_mapping[instrument_id]
            else:
                print(f"Warning: InstrumentID {instrument_id} not found in the mapping.")
            writer.writerow(row)

    print(f"CSV updated and saved to {output_csv}")

# Run the function to update the CSV
update_tickers_in_csv()
