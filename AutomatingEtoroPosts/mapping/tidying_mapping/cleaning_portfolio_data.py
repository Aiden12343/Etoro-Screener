import csv

def clean_portfolio_data(input_file, output_file):
    seen_users = set()
    cleaned_data = []
    current_user = None

    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            user = row[6]
            if user != current_user:
                if user in seen_users:
                    continue  # Skip this row as the user has already been seen
                seen_users.add(user)
                current_user = user
            cleaned_data.append(row)

    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(cleaned_data)

if __name__ == '__main__':
    input_file = 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data.csv'
    output_file = 'AutomatingEtoroPosts/etoro_csv_contents/portfolio_data_cleaned.csv'
    clean_portfolio_data(input_file, output_file)
    print(f"Cleaned data written to {output_file}")