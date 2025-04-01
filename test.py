import re
import pandas as pd

# Define the log file path
log_file_path = "HC_Log_2025-02-24_21-19-14.txt"

# Define table markers
TABLE_MARKERS = {
    "EUTRANCELLFDD STATUS": ("EUTRANCELLFDD STATUS START", "EUTRANCELLFDD STATUS END"),
    "EUTRANCELLFDD CELL SLEEP STATUS": ("EUTRANCELLFDD CELL SLEEP STATUS START", "EUTRANCELLFDD CELL SLEEP STATUS END"),
    "HARDWARE INVENTORY": ("HARDWARE INVENTORY START", "HARDWARE INVENTORY END"),
    "LTE CELL CONFIG": ("LTE CELL CONFIG START", "LTE CELL CONFIG END"),
    "VSWR SUPERVISION": ("VSWR SUPERVISION START", "VSWR SUPERVISION END"),
    "RRU STATUS": ("RRU STATUS START", "RRU STATUS END"),
    "RILINK STATUS": ("RILINK STATUS START", "RILINK STATUS END"),
    "ANTENNANEARUNIT STATUS": ("ANTENNANEARUNIT STATUS START", "ANTENNANEARUNIT STATUS END"),
}

# Read the log file
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
    return table_data if table_data else None  # Return None if no data found

# Extract tables, ignoring empty ones
tables = {}
for table_name, markers in TABLE_MARKERS.items():
    extracted_data = extract_table(log_data, markers[0], markers[1])
    if extracted_data:
        tables[table_name] = extracted_data

# Function to convert table data to DataFrame
def parse_table(data, columns):
    # Filter out empty rows and non-table data (adjust regex if needed)
    table_data = [row.strip() for row in data if row.strip() and ";" in row]

    # Ensure only required columns are considered
    df = pd.DataFrame([row.split(';')[:len(columns)] for row in table_data], columns=columns)
    
    return df


# Define required columns for merging
lte_status_cols = ["MO", "additionalPlmnReservedList", "administrativeState", "cellBarred", "cellId", "cellRange", "earfcndl", "earfcnul", "operationalState", "primaryPlmnReserved", "rachRootSequence", "tac"]
cell_sleep_cols = ["MO", "sleepMode", "sleepState"]
hardware_cols_1 = ["FRU", "LNH", "BOARD", "RF", "BP", "TX (W/dBm)", "VSWR (RL)", "RX (dBm)", "UEs/gUEs", "Sector/AntennaGroup/Cells (State:CellIds:PCIs)"]
hardware_cols_2 = ["FRU", "LNH", "BOARD", "ST", "FAULT", "OPER", "MAINT", "STAT", "PRODUCTNUMBER", "SERIAL"]
cell_config_cols = ["MO", "cellId", "crsGain", "dlChannelBandwidth", "earfcndl", "freqBand", "isDlOnly", "physicalLayerCellId", "rachRootSequence", "tac"]

# Parse tables
df_lte_status = parse_table(tables.get("EUTRANCELLFDD STATUS", []), lte_status_cols)
df_cell_sleep = parse_table(tables.get("EUTRANCELLFDD CELL SLEEP STATUS", []), cell_sleep_cols)
df_hardware_1 = parse_table(tables.get("HARDWARE INVENTORY", []), hardware_cols_1)
df_hardware_2 = parse_table(tables.get("HARDWARE INVENTORY", []), hardware_cols_2)
df_cell_config = parse_table(tables.get("LTE CELL CONFIG", []), cell_config_cols)

# Merge LTE STATUS and CELL SLEEP STATUS
df_lte_status = df_lte_status.merge(df_cell_sleep, on="MO", how="left")

# Merge HARDWARE INVENTORY tables on common columns
df_vswr = df_hardware_1.merge(df_hardware_2, on=["FRU", "LNH", "BOARD"], how="left")

# Merge LTE CELL CONFIG with LTE STATUS
df_cell_config = df_cell_config.merge(df_lte_status[["MO", "administrativeState", "operationalState"]], on="MO", how="left")

# Save to Excel
output_path = "extracted_tables.xlsx"
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

# Save individual tables
df_lte_status.to_excel(writer, sheet_name="LTE_CELL_STATUS", index=False)
df_vswr.to_excel(writer, sheet_name="VSWR", index=False)
df_cell_config.to_excel(writer, sheet_name="CELL_CONFIG_NAME", index=False)

# Save other extracted tables
tables_to_save = ["VSWR SUPERVISION", "RRU STATUS", "RILINK STATUS", "ANTENNANEARUNIT STATUS"]
for table_name in tables_to_save:
    if table_name in tables:
        df = parse_table(tables[table_name], tables[table_name][0].split(';'))
        df.to_excel(writer, sheet_name=table_name.replace(" ", "_"), index=False)

writer.close()
print(f"Extracted data saved to {output_path}")
