import botocore
import boto3
import pandas as pd
import duckdb
import os

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

scoring_path               = "s3://greglenane-drive-to-survive/mapping/scoring.csv"
gp_results_path            = "s3://greglenane-drive-to-survive/gp/gp_results.parquet"
gp_results_scored_path     = "s3://greglenane-drive-to-survive/gp/gp_results_scored.parquet"
sprint_results_path        = "s3://greglenane-drive-to-survive/sprint/sprint_results.parquet"
sprint_results_scored_path = "s3://greglenane-drive-to-survive/sprint/sprint_results_scored.parquet"
combined_scoring_path      = "s3://greglenane-drive-to-survive/results_scored.parquet"

# Enable S3 access
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute(f"""
SET s3_region= '{s3_region}';
SET s3_access_key_id= '{s3_access_key_id}';
SET s3_secret_access_key= '{s3_secret_access_key}';
""")

# s3 file check funciton
def s3_file_exists(s3_path):
    # parse the path we are checking a file in
    s3_url = s3_path.replace("s3://", "").split("/", 1)
    bucket = s3_url[0]
    key = s3_url[1]
    
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError:
        return False

print("Begin score-results.py")

###########################################################################################
# SCORE RESULTS (GP RESULTS)
###########################################################################################

gp_results_scored = con.execute(f"""
                                
        SELECT 
            results.*, 
            s.gp,
            s_exp.gp AS gp_expected,
            fl.fastest_lap,
        FROM read_parquet('{gp_results_path}') results
        LEFT JOIN read_csv_auto('{scoring_path}') s
            ON results.position = s.position
        LEFT JOIN read_csv_auto('{scoring_path}') s_exp
            ON results.grid = s_exp.position
        LEFT JOIN read_csv_auto('{scoring_path}') fl
            ON results.FastestLap_rank = fl.position
        ORDER BY results.round, cast(results.position AS INT) ASC

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
# SCORE RESULTS (SPRINT RESULTS)
###########################################################################################

s3 = boto3.client(
    's3',
    region_name=s3_region,
    aws_access_key_id=s3_access_key_id,
    aws_secret_access_key=s3_secret_access_key
)

if s3_file_exists(sprint_results_path):
    sprint_results_scored = con.execute(f"""

            SELECT 
                results.*, 
                s.sprint,
                s_exp.sprint AS sprint_expected
            FROM read_parquet('{sprint_results_path}') results
            LEFT JOIN read_csv_auto('{scoring_path}') s
                ON results.position = s.position
            LEFT JOIN read_csv_auto('{scoring_path}') s_exp
                ON results.grid = s_exp.position

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
else:
    print("No Sprint results available yet.")

###########################################################################################
# SCORE RESULTS (GP + SPRINT COMBINED)
###########################################################################################
s3 = boto3.client(
    's3',
    region_name=s3_region,
    aws_access_key_id=s3_access_key_id,
    aws_secret_access_key=s3_secret_access_key
)

if s3_file_exists(sprint_results_scored_path):
    combined_scoring = con.execute(f"""
        SELECT 
            gp.number, 
            gp.positionText, 
            gp.points, 
            gp.laps, 
            gp.status, 
            gp.Driver_driverId, 
            gp.Driver_permanentNumber, 
            gp.Driver_code, 
            gp.Driver_url, 
            gp.Driver_givenName, 
            gp.Driver_familyName, 
            gp.Driver_dateOfBirth, 
            gp.Driver_nationality, 
            gp.Constructor_constructorId, 
            gp.Constructor_url, 
            gp.Constructor_name, 
            gp.Constructor_nationality, 
            gp.Time_millis, 
            gp.Time_time, 
            gp.FastestLap_lap, 
            gp.FastestLap_Time_time, 
            gp.season, gp.round, 
            gp.raceName, 
            gp.Circuit_circuitName, 
            gp.Circuit_Location_locality, 
            gp.date,
            sprint.points AS sprint_points,
            sprint.time AS sprint_time,

            gp.grid AS gp_grid,
            gp.gp_expected,
            gp.position AS gp_position,                      
            gp.gp,
            COALESCE(gp.gp, 0) - COALESCE(gp.gp_expected, 0) AS gp_var,

            gp.FastestLap_rank AS fastest_lap_rank,
            gp.fastest_lap,

            sprint.grid AS sprint_grid,
            sprint.sprint_expected,
            sprint.position AS sprint_position, 
            sprint.sprint,
            COALESCE(sprint.sprint, 0) - COALESCE(sprint.sprint_expected, 0) AS sprint_var,

            COALESCE(gp.gp, 0) + COALESCE(gp.fastest_lap, 0) + COALESCE(sprint.sprint, 0) AS total,
            COALESCE(gp.gp_expected, 0) + COALESCE(sprint.sprint_expected, 0) AS total_expected,
            (COALESCE(gp.gp, 0) - COALESCE(gp.gp_expected, 0)) + 
                (COALESCE(sprint.sprint, 0) - COALESCE(sprint.sprint_expected, 0)) AS total_var

        FROM read_parquet('{gp_results_scored_path}') gp
        LEFT JOIN read_parquet('{sprint_results_scored_path}') sprint
            ON gp.round = sprint.round AND gp.Driver_driverId = sprint.Driver_driverId
    """).df()
else:
    print("No sprint data available. Filling sprint columns with NA.")
    combined_scoring = con.execute(f"""
        SELECT 
            gp.number, 
            gp.positionText, 
            gp.points, 
            gp.laps, 
            gp.status, 
            gp.Driver_driverId, 
            gp.Driver_permanentNumber, 
            gp.Driver_code, 
            gp.Driver_url, 
            gp.Driver_givenName, 
            gp.Driver_familyName, 
            gp.Driver_dateOfBirth, 
            gp.Driver_nationality, 
            gp.Constructor_constructorId, 
            gp.Constructor_url, 
            gp.Constructor_name, 
            gp.Constructor_nationality, 
            gp.Time_millis, 
            gp.Time_time, 
            gp.FastestLap_lap, 
            gp.FastestLap_Time_time, 
            gp.season, gp.round, 
            gp.raceName, 
            gp.Circuit_circuitName, 
            gp.Circuit_Location_locality, 
            gp.date,
            NULL AS sprint_points,
            NULL AS sprint_time,
                                   
            gp.grid AS gp_grid,
            gp.gp_expected,
            gp.position AS gp_position, 
            gp.gp,
            COALESCE(gp.gp, 0) - COALESCE(gp.gp_expected, 0) AS gp_var,

            gp.FastestLap_rank AS fastest_lap_rank,
            gp.fastest_lap,
                                   
            NULL AS sprint_grid,
            NULL AS sprint_expected,
            NULL AS sprint_position, 
            NULL AS sprint,
            0 AS sprint_var,
                                   
            COALESCE(gp.gp, 0) + COALESCE(gp.fastest_lap, 0) + 0 AS total,
            COALESCE(gp.gp_expected, 0) + 0 AS total_expected,
            (COALESCE(gp.gp, 0) - COALESCE(gp.gp_expected, 0)) + 0 AS total_var
                                   
        FROM read_parquet('{gp_results_scored_path}') gp
    """).df()

# Register the flattened sprint data as a DuckDB table
con.register("combined_scoring", combined_scoring)

# Persist the flattened sprint data back to S3
con.execute(f"""
COPY combined_scoring
TO '{combined_scoring_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")

print("Combined scored results saved to S3 successfully.")