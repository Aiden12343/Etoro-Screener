import json

# Function to remove duplicates from JSON data
def remove_duplicates(json_data):
    unique_values = {}
    seen_values = set()

    for key, value in json_data.items():
        if value not in seen_values:
            unique_values[key] = value
            seen_values.add(value)

    return unique_values

if __name__ == "__main__":
    try:
        # Path to the JSON file
        file_path = "AutomatingEtoroPosts/mapping/cid_mapping.json"

        # Read the JSON file
        with open(file_path, "r") as file:
            input_json = json.load(file)

        # Remove duplicates
        output_json = remove_duplicates(input_json)

        # Write the result back to the file
        with open(file_path, "w") as file:
            json.dump(output_json, file, indent=4)

        print("Duplicates removed and file updated.")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e.msg} at line {e.lineno} column {e.colno}")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
