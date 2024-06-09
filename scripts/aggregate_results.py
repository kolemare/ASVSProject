from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook


def execute_hive_query(query):
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    hook.run(sql=query)
    print("Executed query successfully")


def aggregate_results_from_batches():
    # Example of aggregation query for avg_temp_by_prov_month
    query_aggregate_avg_temp = """
    INSERT OVERWRITE TABLE avg_temp_by_prov_month
    SELECT
        prov,
        year,
        month,
        AVG(avg_temp) AS avg_temp
    FROM avg_temp_by_prov_month
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_avg_temp)

    # Example of aggregation query for seasonal_trends_by_prov
    query_aggregate_seasonal_trends = """
    INSERT OVERWRITE TABLE seasonal_trends_by_prov
    SELECT
        prov,
        year,
        season,
        AVG(avg_temp) AS avg_temp,
        AVG(avg_wind_speed) AS avg_wind_speed
    FROM seasonal_trends_by_prov
    GROUP BY prov, year, season
    """
    execute_hive_query(query_aggregate_seasonal_trends)

    # Example of aggregation query for temp_humidity_correlation_by_prov_month
    query_aggregate_temp_humidity_correlation = """
    INSERT OVERWRITE TABLE temp_humidity_correlation_by_prov_month
    SELECT
        prov,
        year,
        month,
        AVG(correlation) AS correlation
    FROM temp_humidity_correlation_by_prov_month
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_temp_humidity_correlation)

    # Aggregation for new tables
    query_aggregate_thermal_humidity_index = """
    INSERT OVERWRITE TABLE thermal_humidity_index_by_prov_month
    SELECT
        prov,
        year,
        month,
        AVG(thi) AS thi
    FROM thermal_humidity_index_by_prov_month
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_thermal_humidity_index)

    query_aggregate_wind_direction_distribution = """
    INSERT OVERWRITE TABLE wind_direction_distribution_by_prov
    SELECT
        prov,
        wind_direction,
        SUM(count) AS count
    FROM wind_direction_distribution_by_prov
    GROUP BY prov, wind_direction
    """
    execute_hive_query(query_aggregate_wind_direction_distribution)

    query_aggregate_pressure_extremes = """
    INSERT OVERWRITE TABLE pressure_extremes_by_prov
    SELECT
        prov,
        year,
        month,
        MAX(max_stp) AS max_stp,
        MIN(min_stp) AS min_stp
    FROM pressure_extremes_by_prov
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_pressure_extremes)

    query_aggregate_temp_variability = """
    INSERT OVERWRITE TABLE temp_variability_by_prov
    SELECT
        prov,
        year,
        month,
        AVG(temp_stddev) AS temp_stddev
    FROM temp_variability_by_prov
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_temp_variability)

    query_aggregate_solar_radiation = """
    INSERT OVERWRITE TABLE solar_radiation_by_prov
    SELECT
        prov,
        year,
        month,
        AVG(avg_gbrd) AS avg_gbrd
    FROM solar_radiation_by_prov
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_solar_radiation)

    query_aggregate_avg_dew_point = """
    INSERT OVERWRITE TABLE avg_dew_point_by_prov
    SELECT
        prov,
        year,
        month,
        AVG(avg_dewp) AS avg_dewp
    FROM avg_dew_point_by_prov
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_avg_dew_point)

    query_aggregate_avg_wind_speed = """
    INSERT OVERWRITE TABLE avg_wind_speed_by_prov
    SELECT
        prov,
        year,
        month,
        AVG(avg_wdsp) AS avg_wdsp
    FROM avg_wind_speed_by_prov
    GROUP BY prov, year, month
    """
    execute_hive_query(query_aggregate_avg_wind_speed)


if __name__ == "__main__":
    aggregate_results_from_batches()
