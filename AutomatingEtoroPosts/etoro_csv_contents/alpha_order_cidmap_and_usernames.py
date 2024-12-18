import csv
import json

# --- Function to Alphabetically Sort CSV ---
def sort_csv_file(csv_file_path):
    with open(csv_file_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Get the header
        rows = list(reader)    # Read the rest of the rows
    
    # Sort rows by the username (assuming it's the last column)
    rows.sort(key=lambda x: x[-1])

    # Write back the sorted data to the CSV file
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)  # Write the header
        writer.writerows(rows)   # Write the sorted rows

# --- Function to Alphabetically Sort JSON ---
def sort_json_file(json_file_path):
    with open(json_file_path, 'r', encoding="utf-8") as f:
        cid_mapping = json.load(f)
    
    # Sort the dictionary by keys
    sorted_cid_mapping = {k: cid_mapping[k] for k in sorted(cid_mapping)}

    # Write the sorted data back to the JSON file
    with open(json_file_path, 'w', encoding="utf-8") as f:
        json.dump(sorted_cid_mapping, f, indent=4)

# --- Main Function ---
def main():
    # File paths
    csv_file_path = 'AutomatingEtoroPosts/etoro_csv_contents/etoro_usernames.csv'
    json_file_path = 'AutomatingEtoroPosts/mapping/cid_mapping.json'
    portfolio_csv_file_path = 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv'

    # Sort the files
    print("Sorting CSV file...")
    sort_csv_file(csv_file_path)
    print(f"Sorted {csv_file_path}")

    print("Sorting portfolio data CSV file...")
    sort_csv_file(portfolio_csv_file_path)  # Sort portfolio data CSV by username
    print(f"Sorted {portfolio_csv_file_path}")

    print("Sorting JSON file...")
    sort_json_file(json_file_path)
    print(f"Sorted {json_file_path}")

if __name__ == "__main__":
    main()
