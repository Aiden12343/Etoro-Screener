import csv

# Sample raw text data
raw_text = """
--- Processing Row 6 ---
Raw row text: Ticker_Short_Form
Ticker_Long_Form
Direction_Of_Trade
Percent_Exposure
Percent_PL
Percent_Total_Value
--> Ignore rest of raw text data
S
0.0023
B
0.0026
--->
"""

# Extract relevant lines
lines = raw_text.split('\n')
relevant_lines = lines[5:11]

# Process each relevant line
processed_lines = []
for line in relevant_lines:
    if '<' in line:
        line = line.replace('<', '')
    processed_lines.append(line)

# Write to CSV
with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Ticker_Short_Form", "Ticker_Long_Form", "Direction_Of_Trade", "Percent_Exposure", "Percent_PL", "Percent_Total_Value"])
    writer.writerow(processed_lines)

print("CSV file created successfully!")
