from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook
import sys


def execute_hive_query(query):
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    hook.run(sql=query)
    print("Executed query successfully")


def process_data_for_batch(batch_index, batch_size):
    query_offset = batch_index * batch_size
    query_limit = batch_size

    # Queries for each processing step
    query_avg_temp = f"""
    INSERT INTO TABLE avg_temp_by_prov_month
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        AVG(temp) AS avg_temp
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query_avg_temp)

    query_seasonal_trends = f"""
    WITH seasons AS (
        SELECT *,
        CASE
            WHEN MONTH(`date`) IN (12, 1, 2) THEN 'Winter'
            WHEN MONTH(`date`) IN (3, 4, 5) THEN 'Spring'
            WHEN MONTH(`date`) IN (6, 7, 8) THEN 'Summer'
            WHEN MONTH(`date`) IN (9, 10, 11) THEN 'Fall'
        END AS season
        FROM climate_data
        WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    )
    INSERT INTO TABLE seasonal_trends_by_prov
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
    execute_hive_query(query_seasonal_trends)

    query_temp_humidity_correlation = f"""
    WITH temp_humidity_data AS (
        SELECT
            prov,
            YEAR(`date`) AS year,
            MONTH(`date`) AS month,
            temp,
            hmdy
        FROM climate_data
        WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
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
    INSERT INTO TABLE temp_humidity_correlation_by_prov_month
    SELECT
        prov,
        year,
        month,
        correlation
    FROM correlation_calculations
    ORDER BY prov, year, month
    """
    execute_hive_query(query_temp_humidity_correlation)

    query_thermal_humidity_index = f"""
    INSERT INTO TABLE thermal_humidity_index_by_prov_month
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        AVG(temp - ((0.55 - 0.0055 * hmdy) * (temp - 14.5))) AS thi
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query_thermal_humidity_index)

    query_wind_direction_distribution = f"""
    INSERT INTO TABLE wind_direction_distribution_by_prov
    SELECT
        prov,
        CASE
            WHEN wdct BETWEEN 0 AND 45 THEN 'N'
            WHEN wdct BETWEEN 46 AND 135 THEN 'E'
            WHEN wdct BETWEEN 136 AND 225 THEN 'S'
            WHEN wdct BETWEEN 226 AND 315 THEN 'W'
            ELSE 'N'
        END AS wind_direction,
        COUNT(*) AS count
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, 
        CASE
            WHEN wdct BETWEEN 0 AND 45 THEN 'N'
            WHEN wdct BETWEEN 46 AND 135 THEN 'E'
            WHEN wdct BETWEEN 136 AND 225 THEN 'S'
            WHEN wdct BETWEEN 226 AND 315 THEN 'W'
            ELSE 'N'
        END
    ORDER BY prov, wind_direction
    """
    execute_hive_query(query_wind_direction_distribution)

    query_pressure_extremes = f"""
    INSERT INTO TABLE pressure_extremes_by_prov
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        MAX(stp) AS max_stp,
        MIN(stp) AS min_stp
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query_pressure_extremes)

    query_temp_variability = f"""
    INSERT INTO TABLE temp_variability_by_prov
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        STDDEV(temp) AS temp_stddev
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query_temp_variability)

    query_solar_radiation = f"""
    INSERT INTO TABLE solar_radiation_by_prov
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        AVG(gbrd) AS avg_gbrd
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query_solar_radiation)

    query_avg_dew_point = f"""
    INSERT INTO TABLE avg_dew_point_by_prov
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        AVG(dewp) AS avg_dewp
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query_avg_dew_point)

    query_avg_wind_speed = f"""
    INSERT INTO TABLE avg_wind_speed_by_prov
    SELECT
        prov,
        YEAR(`date`) AS year,
        MONTH(`date`) AS month,
        AVG(wdsp) AS avg_wdsp
    FROM climate_data
    WHERE prov IN (SELECT DISTINCT prov FROM climate_data LIMIT {query_limit} OFFSET {query_offset})
    GROUP BY prov, YEAR(`date`), MONTH(`date`)
    ORDER BY prov, year, month
    """
    execute_hive_query(query_avg_wind_speed)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_batch.py <batch_index> <batch_size>")
        sys.exit(1)

    batch_index = int(sys.argv[1])
    batch_size = int(sys.argv[2])
    process_data_for_batch(batch_index, batch_size)
