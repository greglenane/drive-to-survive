import pandas as pd
import duckdb
import os

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

gp_results_path      = "s3://greglenane-drive-to-survive/gp/gp_results.parquet"
sprint_results_path  = "s3://greglenane-drive-to-survive/sprint/sprint_results.parquet"

print("Begin check-missing-results.py")

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

# Load gp_results data
gp_results = con.execute(f"SELECT * FROM read_parquet('{gp_results_path}')").df()

# Check record count per round
records_per_round = gp_results.groupby('round').size()

if not (records_per_round == 20).all():
    print("WARNING: Not all rounds have exactly 20 records")
    for round_number, count in records_per_round.items():
        if count != 20:
            print(f"Round {round_number} has {count} results")

# Check for gaps in round numbers
rounds = sorted([int(x) for x in gp_results['round'].unique()])
expected_rounds = set(range(int(min(rounds)), int(max(rounds)) + 1))
actual_rounds = set(rounds)
missing_rounds = expected_rounds - actual_rounds

if missing_rounds:
    print(f"WARNING: Missing round numbers: {str(sorted(missing_rounds))}")
else:
    print("There are no missing rounds in GP results")

# Load sprint_results data
sprint_results = con.execute(f"SELECT * FROM read_parquet('{sprint_results_path}')").df()

# check record count per sprint round
sprint_records_per_round = sprint_results.groupby('round').size()
print(f"Sprint rounds with results: {sorted(int(x) for x in sprint_records_per_round.index.tolist())}")

if not (sprint_records_per_round == 20).all():
    print("WARNING: Not all sprint rounds have exactly 20 records")
    for round_number, count in sprint_records_per_round.items():
        if count != 20:
            print(f"Sprint Round {round_number} has {count} picks")
else:
    print("All sprint rounds have exactly 20 records")