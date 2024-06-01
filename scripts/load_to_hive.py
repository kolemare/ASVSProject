from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook

def create_hive_table():
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    query = """
    CREATE TABLE IF NOT EXISTS climate_data (
        `date` STRING,
        hour STRING,
        prcp FLOAT,
        stp FLOAT,
        smax FLOAT,
        smin FLOAT,
        gbrd FLOAT,
        temp FLOAT,
        dewp FLOAT,
        tmax FLOAT,
        tmin FLOAT,
        dmax FLOAT,
        dmin FLOAT,
        hmax FLOAT,
        hmin FLOAT,
        hmdy FLOAT,
        wdct FLOAT,
        gust FLOAT,
        wdsp FLOAT,
        regi STRING,
        prov STRING,
        wsnm STRING,
        inme STRING,
        lat FLOAT,
        lon FLOAT,
        elvt FLOAT
    )
    STORED AS PARQUET
    LOCATION '/data/curated'
    """
    hook.run(sql=query)
    print("Hive table created successfully.")

def load_data_to_hive():
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    query = "LOAD DATA INPATH '/data/transform' INTO TABLE climate_data"
    hook.run(sql=query)
    print("Data loaded into Hive table successfully.")
