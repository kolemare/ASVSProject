import sys
from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook


def execute_hive_query(query):
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    hook.run(sql=query)
    print("Executed query successfully")


def create_temp_humidity_correlation_table():
    query = """
    CREATE TABLE IF NOT EXISTS temp_humidity_correlation_by_prov_month (
        prov STRING,
        year INT,
        month INT,
        correlation DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/temp_humidity_correlation_by_prov_month'
    """
    execute_hive_query(query)


def insert_temp_humidity_correlation_data():
    query = """
    WITH temp_humidity_data AS (
        SELECT
            prov,
            YEAR(`date`) AS year,
            MONTH(`date`) AS month,
            temp,
            hmdy
        FROM climate_data
    ),
    correlation_calculations AS (
        SELECT
            prov,
            year,
            month,
            CORR(temp, hmdy) AS correlation
        FROM temp_humidity_data
        GROUP BY prov, year, month
    )
    INSERT OVERWRITE TABLE temp_humidity_correlation_by_prov_month
    SELECT
        prov,
        year,
        month,
        correlation
    FROM correlation_calculations
    ORDER BY prov, year, month
    """
    execute_hive_query(query)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calculate_temp_humidity_correlation.py <query_type>")
        sys.exit(1)

    query_type = sys.argv[1]
    if query_type == "create_table":
        create_temp_humidity_correlation_table()
    elif query_type == "insert_data":
        insert_temp_humidity_correlation_data()
    else:
        print("Unknown query type. Use 'create_table' or 'insert_data'")
        sys.exit(1)
