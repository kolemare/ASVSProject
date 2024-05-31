import jaydebeapi
import pandas as pd

# JDBC connection properties
driver = 'org.apache.hive.jdbc.HiveDriver'
url = 'jdbc:hive2://hive-server:10000/default'
driver_path = '/opt/airflow/jdbc/hive-jdbc-standalone.jar'


def create_hive_table():
    conn = jaydebeapi.connect(driver, url, ['username', 'password'], driver_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS climate_data (
        date STRING,
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
    LOCATION '/data/curated';
    """)
    cursor.close()
    conn.close()
    print("Hive table created successfully.")


def load_data_to_hive():
    conn = jaydebeapi.connect(driver, url, ['username', 'password'], driver_path)
    cursor = conn.cursor()
    cursor.execute("LOAD DATA INPATH '/data/transform' INTO TABLE climate_data")
    cursor.close()
    conn.close()
    print("Data loaded into Hive table successfully.")


if __name__ == "__main__":
    create_hive_table()
    load_data_to_hive()
