import pandas as pd
import duckdb
import os


# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

picks_season_path          = "s3://greglenane-drive-to-survive/picks/picks_season.parquet"
combined_scoring_path      = "s3://greglenane-drive-to-survive/results_scored.parquet"
picks_scored_path          = "s3://greglenane-drive-to-survive/picks_scored.parquet"
scoring_aggregate_path     = "s3://greglenane-drive-to-survive/scored_aggregate.parquet"
teams_path                 = "s3://greglenane-drive-to-survive/mapping/teams.csv"

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

print("Begin picks-scored.py")

###########################################################################################
# PART 8: SCORE PICKS
###########################################################################################

picks_scored = con.execute(f"""
    SELECT 
        pics.*,
        teams.*,
        cs.*
    FROM read_parquet('{picks_season_path}') pics
    LEFT JOIN read_csv_auto('{teams_path}') teams
        ON pics.Name = teams.Name
    LEFT JOIN read_parquet('{combined_scoring_path}') cs
        ON pics.round = cs.round AND 
        pics.Driver = CONCAT(cs.Driver_givenName, ' ', cs.Driver_familyName);
""").df()

# Register the flattened sprint data as a DuckDB table
con.register("picks_scored", picks_scored)

# Persist the flattened sprint data back to S3
con.execute(f"""
COPY picks_scored
TO '{picks_scored_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")

print("Picks scored results saved to S3 successfully.")

################################################################################
# PART 9: SUMMARIZE PICKS SCORED
################################################################################
scoring_aggregate = con.execute(f"""
    WITH round_totals AS (
        SELECT 
            Name, 
            Team,
            Team_Name,
            Round,
            Race,
            DATE,
            Driver,
            Constructor_name AS Constructor,
            gp_grid,
            gp_expected,
            gp_position,                      
            gp,
            gp_var,
            fastest_lap_rank,
            fastest_lap,
            sprint_grid,
            sprint_expected,
            sprint_position, 
            sprint,
            sprint_var,
            total,
            total_expected,
            total_var
        FROM read_parquet('{picks_scored_path}')
        /* Grouping here ensures we have one row per player per round */
        GROUP BY ALL 
    )
    SELECT 
        *,
        SUM(total) OVER (
            PARTITION BY Name 
            ORDER BY Round 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_total,
        SUM(total_expected) OVER (
            PARTITION BY Name 
            ORDER BY Round 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_expected,
        SUM(total_var) OVER (
            PARTITION BY Name 
            ORDER BY Round 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_var
    FROM round_totals
    ORDER BY Round ASC, cumulative_total DESC, Name
""").df()

# Register the flattened sprint data as a DuckDB table
con.register("scoring_aggregate", scoring_aggregate)

# Persist the flattened sprint data back to S3
con.execute(f"""
COPY scoring_aggregate
TO '{scoring_aggregate_path}' 
(FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
""")

print("Scoring aggregate saved to S3 successfully.")

print("drive-to-survive pipeline completed successfully.")
