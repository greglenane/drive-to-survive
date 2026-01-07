import requests
import pandas as pd
import duckdb
import yaml  
import ast
import yaml

# set variables
rnd = "24"
year = "2025"
gp_api_temp_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_temp.parquet"
gp_api_main_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_main.parquet"
gp_results_path      = "s3://greglenane-drive-to-survive/gp/gp_results.parquet"
sprint_api_temp_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_temp.parquet"
sprint_api_main_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_main.parquet"
sprint_results_path  = "s3://greglenane-drive-to-survive/sprint/sprint_results.parquet"



# functions
# Robust Parser for DuckDB-stringified JSON
def robust_parse(val):
    # check for null/NaN
    if pd.isna(val):
        return []
    # If the data is already a list or a dictionary return as is
    if isinstance(val, (list, dict)):
        return val
    # if list is a string, try to parse it
    if isinstance(val, str):
        try:
            # safe_load handles the unquoted strings and date-logic
            return yaml.safe_load(val)
        except Exception:
            return []
    return val

print(f"Starting ETL process for Round {rnd}, Year {year}")

###########################################################################################
# PART 1: INGESTION (GP RESULTS)
###########################################################################################
gp_url = f"https://api.jolpi.ca/ergast/f1/{year}/{rnd}/results/"
gp_data = requests.get(gp_url).json()
gp_api = pd.json_normalize(gp_data)
gp_api.columns = [c.replace(".", "_") for c in gp_api.columns]
print("GP API data retrieved successfully.")

con.register("gp_api_temp", gp_api)
con.execute(f"COPY gp_api_temp TO '{gp_api_temp_path}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)")

con.execute("DROP TABLE IF EXISTS gp_api_main")
try:
    con.execute(f"CREATE TABLE gp_api_main AS SELECT * FROM read_parquet('{gp_api_main_path}')")
except Exception:
    con.execute("CREATE TABLE gp_api_main AS SELECT * FROM gp_api_temp")

con.execute("""
MERGE INTO gp_api_main AS main
USING gp_api_temp AS temp
ON main.MRData_RaceTable_round = temp.MRData_RaceTable_round
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")

con.execute(f"COPY gp_api_main TO '{gp_api_main_path}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)")

print("GP API data merged and saved successfully.")
###########################################################################################
# PART 2: INGESTION (SPRINT RESULTS)
###########################################################################################
sprint_url = f"https://api.jolpi.ca/ergast/f1/{year}/{rnd}/sprint/"
sprint_data = requests.get(sprint_url).json()
sprint_api = pd.json_normalize(sprint_data)
sprint_api.columns = [c.replace(".", "_") for c in sprint_api.columns]
print("Sprint API data retrieved successfully.")

if sprint_api.at[0, 'MRData_RaceTable_Races']:
    con.register('sprint_api_temp', sprint_api)
    con.execute(f"COPY sprint_api_temp TO '{sprint_api_temp_path}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)")
    
    con.execute("DROP TABLE IF EXISTS sprint_api_main")
    try:
        con.execute(f"CREATE TABLE sprint_api_main AS SELECT * FROM read_parquet('{sprint_api_main_path}')")
    except Exception:
        con.execute("CREATE TABLE sprint_api_main AS SELECT * FROM sprint_api_temp")

    con.execute("""
    MERGE INTO sprint_api_main AS main
    USING sprint_api_temp AS temp
    ON main.MRData_RaceTable_round = temp.MRData_RaceTable_round
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """)
    con.execute(f"COPY sprint_api_main TO '{sprint_api_main_path}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)")
    print("Sprint API data merged and saved successfully.")
###########################################################################################
# PART 3: FLATTENING & TRANSFORMATION (GP RESULTS)
###########################################################################################

# 1. Load the merged data back from S3
gp_main = con.execute(f"SELECT * FROM read_parquet('{gp_api_main_path}')").df()

# 2. Parse
gp_main['MRData_RaceTable_Races'] = gp_main['MRData_RaceTable_Races'].apply(robust_parse)

# 3. Explode the list of races
gp_exploded = gp_main.explode('MRData_RaceTable_Races').dropna(subset=['MRData_RaceTable_Races'])

flat_data = pd.json_normalize(
    gp_exploded['MRData_RaceTable_Races'],
    record_path=['Results'],
    meta=[
        'season', 
        'round', 
        'raceName', 
        ['Circuit', 'circuitName'],
        ['Circuit', 'Location', 'locality'],
        'date'
    ],
    errors='ignore'
)

# 5. Clean up column names
flat_data.columns = [c.replace('.', '_') for c in flat_data.columns]
# 6. Register the flattened data as a DuckDB table
con.register("flat_data_table", flat_data)

# 7. Persist the flattened data back to S3
con.execute(f"""
COPY flat_data_table 
TO '{gp_results_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")
print("Flattened GP results data saved to S3 successfully.")

###########################################################################################
# PART 4: FLATTENING & TRANSFORMATION (SPRINT RESULTS)
###########################################################################################

# 1. Load the merged sprint data back from S3
sprint_main = con.execute(f"SELECT * FROM read_parquet('{sprint_api_main_path}')").df()

# 2. Parse
sprint_main['MRData_RaceTable_Races'] = sprint_main['MRData_RaceTable_Races'].apply(robust_parse)

# 3. Explode the list of sprints
sprint_exploded = sprint_main.explode('MRData_RaceTable_Races').dropna(subset=['MRData_RaceTable_Races'])

sprint_flat_data = pd.json_normalize(
    sprint_exploded['MRData_RaceTable_Races'],
    record_path=['SprintResults'],              
    meta=[
        'season', 
        'round', 
        'raceName', 
        ['Circuit', 'circuitName'],
        ['Circuit', 'Location', 'locality'],
        'date'
    ],
    errors='ignore'
)

# 5. Clean up column names
sprint_flat_data.columns = [c.replace('.', '_') for c in sprint_flat_data.columns]

# 6. Register the flattened sprint data as a DuckDB table
con.register("sprint_flat_data_table", sprint_flat_data)

# 7. Persist the flattened sprint data back to S3
con.execute(f"""
COPY sprint_flat_data_table
TO '{sprint_results_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")

print("Flattened Sprint results data saved to S3 successfully.")