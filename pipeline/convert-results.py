import pandas as pd
import duckdb
import yaml
import os
import boto3
import botocore

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

gp_api_main_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_main.parquet"
gp_results_path      = "s3://greglenane-drive-to-survive/gp/gp_results.parquet"
sprint_api_main_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_main.parquet"
sprint_results_path  = "s3://greglenane-drive-to-survive/sprint/sprint_results.parquet"

# Enable S3 access
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute(f"""
SET s3_region= '{s3_region}';
SET s3_access_key_id= '{s3_access_key_id}';
SET s3_secret_access_key= '{s3_secret_access_key}';
""")

print("Begin convert-results.py")

# parser fucntion for JSON
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

# s3 file check funciton
def s3_file_exists(s3_path):
    # parse the path we are checking a file in
    s3_url = s3_path.replace("s3://", "").split("/", 1)
    bucket = s3_url[0]
    key = s3_url[1]
    
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError:
        return False

print(f"Beginning conversion process")

###########################################################################################
# FLATTENING & TRANSFORMATION (GP RESULTS)
###########################################################################################

# Load the merged data back from S3
gp_main = con.execute(f"SELECT * FROM read_parquet('{gp_api_main_path}')").df()

# Parse
gp_main['MRData_RaceTable_Races'] = gp_main['MRData_RaceTable_Races'].apply(robust_parse)

# Explode the list of races
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

# Clean up column names
flat_data.columns = [c.replace('.', '_') for c in flat_data.columns]
# Register the flattened data as a DuckDB table
con.register("flat_data_table", flat_data)

# Persist the flattened data back to S3
con.execute(f"""
COPY flat_data_table 
TO '{gp_results_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")
print("Flattened GP results data saved to S3 successfully.")

###########################################################################################
# FLATTENING & TRANSFORMATION (SPRINT RESULTS)
###########################################################################################

if s3_file_exists(sprint_api_main_path):
    # Load the merged sprint data back from S3
    sprint_main = con.execute(f"SELECT * FROM read_parquet('{sprint_api_main_path}')").df()
    # Parse
    sprint_main['MRData_RaceTable_Races'] = sprint_main['MRData_RaceTable_Races'].apply(robust_parse)
    # Explode the list of sprints
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
    # Clean up column names
    sprint_flat_data.columns = [c.replace('.', '_') for c in sprint_flat_data.columns]
    # Register the flattened sprint data as a DuckDB table
    con.register("sprint_flat_data_table", sprint_flat_data)
    # Persist the flattened sprint data back to S3
    con.execute(f"""
    COPY sprint_flat_data_table
    TO '{sprint_results_path}' 
    (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
    """)
    print("Flattened Sprint results data saved to S3 successfully.")
else:
    print("No Sprint data available yet.")