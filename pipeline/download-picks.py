import pandas as pd
import requests
import duckdb
import os
import boto3
from io import BytesIO

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

picks_path = "s3://greglenane-drive-to-survive/picks/picks.xlsx"
picks_season_path = "s3://greglenane-drive-to-survive/picks/picks_season.parquet"
bucket_name = "greglenane-drive-to-survive"
s3_xlsx_key = "picks/picks.xlsx"
excel_url = os.getenv('EXCEL_URL') 

print("Begin download-picks.py")

# 2. Download raw bytes from Google Sheets
print("Downloading Excel file")
response = requests.get(excel_url)
excel_bytes = response.content

# 2a. Extract sheet names using Pandas
print("Extracting sheet names")
with BytesIO(excel_bytes) as bio:
    xl = pd.ExcelFile(bio, engine='openpyxl')
    sheet_names = xl.sheet_names

# 3. Upload to S3 using Boto3
print(f"Uploading .xlsx file to {picks_path}")
s3 = boto3.client(
    's3',
    aws_access_key_id=s3_access_key_id,
    aws_secret_access_key=s3_secret_access_key,
    region_name=s3_region
)
s3.put_object(
    Bucket=bucket_name,
    Key=s3_xlsx_key,
    Body=excel_bytes,
    ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

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

all_sheets_list = []

print("Reading and binding sheets")
with BytesIO(excel_bytes) as bio:
    for sheet in sheet_names:
        # Skip specific sheets if necessary (e.g., 'Instructions' or 'Summary')
        if sheet == 'drivers': continue
        
        df_sheet = pd.read_excel(bio, sheet_name=sheet, engine='openpyxl')
        
        # Optional: Add a column to track which sheet the data came from
        df_sheet['source_sheet'] = sheet
        
        all_sheets_list.append(df_sheet)

# Bind (concatenate) all DataFrames together
final_df = pd.concat(all_sheets_list, ignore_index=True)

# 4. Upload the Pandas DataFrame directly to S3 as Parquet
max_round = max(int(x) for x in sheet_names if x != 'drivers')

print(f"There are now picks through round {max_round}.")
print(f"Uploading picks table to {picks_season_path}")
con.execute(f"COPY final_df TO '{picks_season_path}' (FORMAT PARQUET);")