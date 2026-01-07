import requests
import pandas as pd
import duckdb
import os

# set variables
rnd = "24"
year = "2025"

s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

gp_api_temp_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_temp.parquet"
gp_api_main_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_main.parquet"
sprint_api_temp_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_temp.parquet"
sprint_api_main_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_main.parquet"

# Enable S3 access
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute(f"""
SET s3_region= '{s3_region}';
SET s3_access_key_id= '{s3_access_key_id}';
SET s3_secret_access_key= '{s3_secret_access_key}';
""")

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