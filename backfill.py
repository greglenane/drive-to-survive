# load libraries
import requests
import pandas as pd
import duckdb
<<<<<<< HEAD
<<<<<<< HEAD
import os
import yaml

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

gp_api_temp_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_temp.parquet"
gp_api_main_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_main.parquet"
gp_results_path      = "s3://greglenane-drive-to-survive/gp/gp_results.parquet"
sprint_api_temp_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_temp.parquet"
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
=======
=======
import os
import yaml
>>>>>>> 811a1e9 (updates for secret use and first script run test)

# set variables
s3_region = os.getenv('S3_REGION')
s3_access_key_id = os.getenv('S3_ACCESS_KEY_ID')
s3_secret_access_key = os.getenv('S3_SECRET_ACCESS_KEY')

gp_api_temp_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_temp.parquet"
gp_api_main_path     = "s3://greglenane-drive-to-survive/api/gp/gp_api_main.parquet"
gp_results_path      = "s3://greglenane-drive-to-survive/gp/gp_results.parquet"
sprint_api_temp_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_temp.parquet"
sprint_api_main_path = "s3://greglenane-drive-to-survive/api/sprint/sprint_api_main.parquet"
sprint_results_path  = "s3://greglenane-drive-to-survive/sprint/sprint_results.parquet"

<<<<<<< HEAD

>>>>>>> 08a2c1b (initial setup for gh actions with duckdb method)
=======
# Enable S3 access
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute(f"""
SET s3_region= '{s3_region}';
SET s3_access_key_id= '{s3_access_key_id}';
SET s3_secret_access_key= '{s3_secret_access_key}';
""")
>>>>>>> 811a1e9 (updates for secret use and first script run test)

for rnd in map(str, range(1, 25)):
    print(f"\n================ Round {rnd} ================\n")

    ###########################################################################################
    # Execute GP API request
    gp_url = f"https://api.jolpi.ca/ergast/f1/2025/{rnd}/results/"
    gp_data = requests.get(gp_url).json()
    gp_api = pd.json_normalize(gp_data)
    gp_api.columns = [c.replace(".", "_") for c in gp_api.columns]
    print("GP API data retrieved successfully.")

    # Register temp API data
    con.register("gp_api_temp", gp_api)

    # Always write temp snapshot (audit/debug)
    con.execute(f"""
    COPY gp_api_temp
    TO '{gp_api_temp_path}'
    (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
    """)

    # Drop main table if exists to avoid conflicts
    con.execute("DROP TABLE IF EXISTS gp_api_main")

    # Try to load main table into DuckDB
    try:
        con.execute(f"""
            CREATE TABLE gp_api_main AS
            SELECT * FROM read_parquet('{gp_api_main_path}')
        """)
        print("gp_api_main exists → loaded into DuckDB")
    except Exception:
        print("gp_api_main does not exist → initializing from temp")
        con.execute("""
            CREATE TABLE gp_api_main AS
            SELECT * FROM gp_api_temp
        """)

    # MERGE temp into main
    con.execute("""
    MERGE INTO gp_api_main AS main
    USING gp_api_temp AS temp
    ON main.MRData_RaceTable_round = temp.MRData_RaceTable_round
    WHEN MATCHED THEN
        UPDATE SET *
    WHEN NOT MATCHED THEN
        INSERT *
    """)
    print("GP API data merged successfully.")

    # Persist merged main table
    con.execute(f"""
    COPY gp_api_main
    TO '{gp_api_main_path}'
    (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
    """)
    print("GP API main table saved to S3 successfully.")

    ###########################################################################################
    # execute gp api request
    sprint_url = f"https://api.jolpi.ca/ergast/f1/2025/{rnd}/sprint/"
    sprint_response = requests.get(sprint_url)
    sprint_data = sprint_response.json()
    sprint_api = pd.json_normalize(sprint_data)
    print('Sprint API data retrieved successfully.')

    # rename columns
    sprint_api.columns = [c.replace(".", "_") for c in sprint_api.columns]

    # register api request as duckdb table
    con.register('sprint_api_temp', sprint_api)

    # Inspect the value in that column and check if empty
    sprint_value = sprint_api.at[0, 'MRData_RaceTable_Races']
    if sprint_value == []:
        print("No sprint data available for this round")
    else:
        # Always write temp snapshot (audit/debug)
        con.execute(f"""
        COPY sprint_api_temp
        TO '{sprint_api_temp_path}'
        (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
        """)

        # Drop main table if exists to avoid conflicts
        con.execute("DROP TABLE IF EXISTS sprint_api_main")

        #attempt to load sprint_api_main and if not save temp as main
        try:
            con.execute(f"""
                CREATE TABLE sprint_api_main AS
                SELECT * FROM read_parquet('{sprint_api_main_path}')
            """)
            print("sprint_api_main exists → loaded into DuckDB")
        except Exception:
            print("sprint_api_main does not exist → initializing from temp")
            con.execute("""
                CREATE TABLE sprint_api_main AS
                SELECT * FROM sprint_api_temp
            """)

        # MERGE temp into main
        con.execute("""
        MERGE INTO sprint_api_main AS main
        USING sprint_api_temp AS temp
        ON main.MRData_RaceTable_round = temp.MRData_RaceTable_round
        WHEN MATCHED THEN
            UPDATE SET *
        WHEN NOT MATCHED THEN
            INSERT *
        """)
        print("Sprint API data merged successfully.")

        # Persist merged main table
        con.execute(f"""
        COPY sprint_api_main
        TO '{sprint_api_main_path}'
        (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)
        """)
        print("Sprint API main table saved to S3 successfully.")