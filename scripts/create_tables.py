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


def create_thermal_humidity_index_table():
    query = """
    CREATE TABLE IF NOT EXISTS thermal_humidity_index_by_prov_month (
        prov STRING,
        year INT,
        month INT,
        thi DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/thermal_humidity_index_by_prov_month'
    """
    execute_hive_query(query)


def create_wind_direction_distribution_table():
    query = """
    CREATE TABLE IF NOT EXISTS wind_direction_distribution_by_prov (
        prov STRING,
        wind_direction STRING,
        count INT
    )
    STORED AS PARQUET
    LOCATION '/data/results/wind_direction_distribution_by_prov'
    """
    execute_hive_query(query)


def create_pressure_extremes_table():
    query = """
    CREATE TABLE IF NOT EXISTS pressure_extremes_by_prov (
        prov STRING,
        year INT,
        month INT,
        max_stp DOUBLE,
        min_stp DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/pressure_extremes_by_prov'
    """
    execute_hive_query(query)


def create_temp_variability_table():
    query = """
    CREATE TABLE IF NOT EXISTS temp_variability_by_prov (
        prov STRING,
        year INT,
        month INT,
        temp_stddev DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/temp_variability_by_prov'
    """
    execute_hive_query(query)


def create_solar_radiation_table():
    query = """
    CREATE TABLE IF NOT EXISTS solar_radiation_by_prov (
        prov STRING,
        year INT,
        month INT,
        avg_gbrd DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/solar_radiation_by_prov'
    """
    execute_hive_query(query)


def create_avg_dew_point_table():
    query = """
    CREATE TABLE IF NOT EXISTS avg_dew_point_by_prov (
        prov STRING,
        year INT,
        month INT,
        avg_dewp DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/avg_dew_point_by_prov'
    """
    execute_hive_query(query)


def create_avg_wind_speed_table():
    query = """
    CREATE TABLE IF NOT EXISTS avg_wind_speed_by_prov (
        prov STRING,
        year INT,
        month INT,
        avg_wdsp DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/avg_wind_speed_by_prov'
    """
    execute_hive_query(query)
