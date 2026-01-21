import pandas as pd
import duckdb
import os

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

picks_scored_path = "s3://greglenane-drive-to-survive/picks_scored.parquet"

print("Begin check-na.py")

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

# load picks_scored data
picks_scored = con.execute(f"""
    SELECT 
        *
    FROM read_parquet('{picks_scored_path}')""").df()

# check for NA driver results indicating issue with picks and results join
na_results = picks_scored[picks_scored['positionText'].isna()]
if not na_results.empty:
    print(f"WARNING: Found {len(na_results)} picks with NA driver results")
    na_rounds = na_results[['Name', 'round']].drop_duplicates().values.tolist()
else:
    print("All picks have valid driver results")
    print("Now checking if all picks are properly scored...")
    na_scores = picks_scored[picks_scored['gp'].isna()]
    if not na_scores.empty:
        print(f"WARNING: Found {len(na_scores)} picks with NA scores")
        na_score_rounds = na_scores[['Name', 'round']].drop_duplicates().values.tolist()
    else:
        print("All picks are properly scored")