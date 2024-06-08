import sys
from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook


def execute_hive_query(query):
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    hook.run(sql=query)
    print("Executed query successfully")


def create_avg_temp_table():
    query = """
    CREATE TABLE IF NOT EXISTS avg_temp_by_prov_month (
        prov STRING,
        year INT,
        month INT,
        avg_temp DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/avg_temp_by_prov_month'
    """
    execute_hive_query(query)


def insert_avg_temp_data():
    query = """
    INSERT OVERWRITE TABLE avg_temp_by_prov_month
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        AVG(temp) AS avg_temp
    FROM climate_data
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calculate_avg_temp.py <query_type>")
        sys.exit(1)

    query_type = sys.argv[1]
    if query_type == "create_table":
        create_avg_temp_table()
    elif query_type == "insert_data":
        insert_avg_temp_data()
    else:
        print("Unknown query type. Use 'create_table' or 'insert_data'")
        sys.exit(1)
