import requests
import pandas as pd
import duckdb
import os


# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

schedule_path = "s3://greglenane-drive-to-survive/mapping/schedule.parquet"

# Enable S3 access
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute(f"""
SET s3_region= '{s3_region}';
SET s3_access_key_id= '{s3_access_key_id}';
SET s3_secret_access_key= '{s3_secret_access_key}';
""")

# 1. Fetch data
url = "https://api.jolpi.ca/ergast/f1/2026/races/"
data = requests.get(url).json()

# 2. Normalize and clean columns (removing . and _)
df = pd.json_normalize(data, record_path=["MRData", "RaceTable", "Races"])
df.columns = (
    df.columns
    .str.replace(".", "", regex=False)
    .str.replace("_", "", regex=False)
    .str.lower()
)

# 3. Convert all time/date pairs to US/Eastern
# This finds 'time', 'firstpracticetime', 'qualifyingtime', etc.
time_cols = [col for col in df.columns if 'time' in col]

for t_col in time_cols:
    # Match the date column (e.g., 'qualifyingtime' -> 'qualifyingdate')
    prefix = t_col.replace('time', '')
    d_col = f"{prefix}date"
    
    if d_col in df.columns:
        # Combine strings into one datetime object
        # pd.to_datetime handles 'Z' (UTC) automatically if present
        dt_utc = pd.to_datetime(df[d_col] + ' ' + df[t_col], errors='coerce')
        
        # Ensure it's treated as UTC if no timezone info exists
        if dt_utc.dt.tz is None:
            dt_utc = dt_utc.dt.tz_localize('UTC')
            
        # Convert to US/Eastern (Handles EST vs EDT automatically)
        dt_est = dt_utc.dt.tz_convert('US/Eastern')
        
        # Save back as new columns
        # Main race will use 'race' prefix, others use their original (e.g., 'qualifying')
        clean_prefix = prefix if prefix != '' else 'race'
        df[f"{clean_prefix}date_est"] = dt_est.dt.date
        df[f"{clean_prefix}time_est"] = dt_est.dt.strftime('%H:%M:%S')

# Register the flattened sprint data as a DuckDB table
con.register("schedule", df)

# Persist the flattened sprint data back to S3
con.execute(f"""
COPY schedule
TO '{schedule_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")

print("Schedule saved to S3 successfully.")