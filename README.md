This project extracts specific table data from telecom-related log files and transforms it into structured Excel sheets for analysis.

📂 Key Components

Extraction Code: Reads the log file and extracts relevant tabular data.

Transformation Code: Cleans and merges extracted data into meaningful tables.

Output: A structured Excel file (extracted_tables.xlsx).

🛠️ Setup Instructions

1️⃣ Prerequisites

Ensure you have the following installed:

Python 3.x

Pandas

XlsxWriter

Install dependencies using:

pip install pandas xlsxwriter

2️⃣ Running the Code

Place the log file (HC_Log_YYYY-MM-DD_HH-MM-SS.txt) in the working directory.

Run the script:

python extract.py
python transform.py

📤 Extraction Process (extract.py)

The extraction code reads and extracts relevant tabular data based on predefined markers.

🔍 How It Works

Reads the log file line by line.

Identifies table sections using start and end markers.

Extracts data within the markers.

Saves extracted tables in memory for transformation.

🚀 Code Structure

# Read log file
with open(log_file_path, "r", encoding="utf-8") as file:
    log_data = file.readlines()

# Function to extract table data
def extract_table(log_data, start_marker, end_marker):
    extracting = False
    table_data = []
    for line in log_data:
        if start_marker in line:
            extracting = True
            continue
        if end_marker in line:
            extracting = False
            break
        if extracting:
            table_data.append(line.strip())
    return table_data if table_data else None

🔄 Transformation Process (transform.py)

The transformation code processes the extracted tables and saves them into structured Excel sheets.

🔍 How It Works

Converts extracted tables into Pandas DataFrames.

Cleans up data by filtering out empty rows.

Ensures correct column alignment.

Merges related tables.

Saves structured data in an Excel file (extracted_tables.xlsx).

🚀 Code Structure

# Function to convert table data to DataFrame
def parse_table(data, columns):
    table_data = [row.strip() for row in data if row.strip() and ";" in row]
    df = pd.DataFrame([row.split(';')[:len(columns)] for row in table_data], columns=columns)
    return df

# Save to Excel
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
df_lte_status.to_excel(writer, sheet_name="LTE_CELL_STATUS", index=False)
df_vswr.to_excel(writer, sheet_name="VSWR", index=False)
df_cell_config.to_excel(writer, sheet_name="CELL_CONFIG_NAME", index=False)
writer.close()

📊 Output File

extracted_tables.xlsx contains structured data in separate sheets:

LTE_CELL_STATUS

VSWR

CELL_CONFIG_NAME

Other extracted tables
