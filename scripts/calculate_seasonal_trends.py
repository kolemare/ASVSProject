import sys
from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook


def execute_hive_query(query):
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    hook.run(sql=query)
    print("Executed query successfully")


def create_seasonal_trends_table():
    query = """
    CREATE TABLE IF NOT EXISTS seasonal_trends_by_prov (
        prov STRING,
        year INT,
        season STRING,
        avg_temp DOUBLE,
        avg_wind_speed DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/seasonal_trends_by_prov'
    """
    execute_hive_query(query)


def insert_seasonal_trends_data():
    query = """
    WITH seasons AS (
        SELECT *,
        CASE
            WHEN MONTH(`date`) IN (12, 1, 2) THEN 'Winter'
            WHEN MONTH(`date`) IN (3, 4, 5) THEN 'Spring'
            WHEN MONTH(`date`) IN (6, 7, 8) THEN 'Summer'
            WHEN MONTH(`date`) IN (9, 10, 11) THEN 'Fall'
        END AS season
        FROM climate_data
    )
    INSERT OVERWRITE TABLE seasonal_trends_by_prov
    SELECT
        prov,
        YEAR(`date`) AS year,
        season,
        AVG(temp) AS avg_temp,
        AVG(wdsp) AS avg_wind_speed
    FROM seasons
    GROUP BY prov, YEAR(`date`), season
    ORDER BY prov, year, season
    """
    execute_hive_query(query)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calculate_seasonal_trends.py <query_type>")
        sys.exit(1)

    query_type = sys.argv[1]
    if query_type == "create_table":
        create_seasonal_trends_table()
    elif query_type == "insert_data":
        insert_seasonal_trends_data()
    else:
        print("Unknown query type. Use 'create_table' or 'insert_data'")
        sys.exit(1)
