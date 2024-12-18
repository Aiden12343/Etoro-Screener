import csv

def remove_duplicates(input_file, output_file=None):
    """
    Reads a CSV file, removes duplicate rows (case-insensitive), and writes the result to a new file.
    Parameters:
        input_file (str): Path to the input CSV file.
        output_file (str, optional): Path to the output CSV file. If None, overwrites the input file.
    """
    try:
        # Use a set to track unique rows
        seen = set()
        rows = []

        # Read the input file
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Read the header
            rows.append(header)   # Keep the header
            for row in reader:
                # Normalize row data to lowercase to ensure case-insensitive comparison
                normalized_row = tuple(value.lower() if isinstance(value, str) else value for value in row)
                
                if normalized_row not in seen:
                    seen.add(normalized_row)
                    rows.append(row)

        # Write to the output file
        output_file = output_file or input_file
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows)

        print(f"Duplicates removed. Cleaned data saved to '{output_file}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_csv = "AutomatingEtoroPosts\etoro_csv_contents\etoro_usernames.csv"  # Replace with your CSV file path
output_csv = None  # Optional, set to None to overwrite input file
remove_duplicates(input_csv, output_csv)
