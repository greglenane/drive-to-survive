import pandas as pd
import duckdb
import os

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

picks_season_path = "s3://greglenane-drive-to-survive/picks/picks_season.parquet"

print("Begin check-missing-picks.py")

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

# Load picks_season data
picks_season = con.execute(f"SELECT * FROM read_parquet('{picks_season_path}')").df()

# get unique rounds
unique_rounds = picks_season['Round'].nunique()

# for each name get the count of picks
missing_picks = picks_season.groupby('Name').size().reset_index(name='pick_count')

# filter for each name that has less picks than rounds
missing_picks = missing_picks[missing_picks['pick_count'] < unique_rounds]


if len(missing_picks) > 0:
    for index, row in missing_picks.iterrows():
        name = row['Name']
        picked_rounds = picks_season[picks_season['Name'] == name]['Round'].unique()
        all_rounds = sorted(picks_season['Round'].unique())
        missing_rounds = [r for r in all_rounds if r not in picked_rounds]
        print(f"{name} is missing picks for round(s): {', '.join(map(str, missing_rounds))}")
else:
    print("All players have picks for all rounds")
