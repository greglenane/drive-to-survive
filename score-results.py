import pandas as pd
import duckdb
import os

# set variables
#s3_region = os.getenv('S3_REGION')
#s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
#s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

scoring_path               = "s3://greglenane-drive-to-survive/mapping/scoring.csv"
gp_results_path            = "s3://greglenane-drive-to-survive/gp/gp_results.parquet"
gp_results_scored_path     = "s3://greglenane-drive-to-survive/gp/gp_results_scored.parquet"
sprint_results_path        = "s3://greglenane-drive-to-survive/sprint/sprint_results.parquet"
sprint_results_scored_path = "s3://greglenane-drive-to-survive/sprint/sprint_results_scored.parquet"

# Enable S3 access
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute(f"""
SET s3_region= '{s3_region}';
SET s3_access_key_id= '{s3_access_key_id}';
SET s3_secret_access_key= '{s3_secret_access_key}';
""")

###########################################################################################
# PART 5: SCORE RESULTS (GP RESULTS)
###########################################################################################
gp_results_scored = con.execute(f"""
                                
        SELECT 
            gp.*, 
            s.gp,
            s_exp.gp AS gp_expected,
            fl.fastest_lap,
        FROM read_parquet('{gp_results_path}') gp
        LEFT JOIN read_csv_auto('{scoring_path}') s
            ON gp.position = s.position
        LEFT JOIN read_csv_auto('{scoring_path}') s_exp
            ON gp.grid = s_exp.position
        LEFT JOIN read_csv_auto('{scoring_path}') fl
            ON gp.FastestLap_rank = fl.position
        ORDER BY gp.round, cast(gp.position AS INT) ASC

    """).df()

# Register the flattened sprint data as a DuckDB table
con.register("gp_results_scored_path", gp_results_scored)

# Persist the flattened sprint data back to S3
con.execute(f"""
COPY gp_results_scored_path
TO '{gp_results_scored_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")

print("Scored GP results saved to S3 successfully.")

###########################################################################################
# PART 6: SCORE RESULTS (SPRINT RESULTS)
###########################################################################################

sprint_results_scored = con.execute(f"""
                                
        SELECT 
            sprint.*, 
            s.sprint,
            s_exp.sprint AS sprint_expected
        FROM read_parquet('{sprint_results_path}') sprint
        LEFT JOIN read_csv_auto('{scoring_path}') s
            ON sprint.position = s.position
        LEFT JOIN read_csv_auto('{scoring_path}') s_exp
            ON sprint.grid = s_exp.position

    """).df()

# Register the flattened sprint data as a DuckDB table
con.register("sprint_results_scored_path", sprint_results_scored)

# Persist the flattened sprint data back to S3
con.execute(f"""
COPY sprint_results_scored_path
TO '{sprint_results_scored_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")

print("Scored Sprint results saved to S3 successfully.")