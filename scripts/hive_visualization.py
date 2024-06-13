import pandas as pd
import matplotlib.pyplot as plt
from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_hive_query(query):
    hook = HiveServer2Hook(hiveserver2_conn_id='hive_server2_default')
    return hook.get_pandas_df(query)


def create_visualizations():
    queries = {
        "avg_temp_by_prov_month": "SELECT * FROM avg_temp_by_prov_month",
        "seasonal_trends_by_prov": "SELECT * FROM seasonal_trends_by_prov",
        "temp_humidity_correlation_by_prov_month": "SELECT * FROM temp_humidity_correlation_by_prov_month"
    }

    data = {table: execute_hive_query(query) for table, query in queries.items()}

    # Print the columns of each dataframe for debugging
    for table, df in data.items():
        logger.info(f"Columns in {table}: {df.columns.tolist()}")

    results_path = '/opt/airflow/results'
    os.makedirs(results_path, exist_ok=True)

    # Strip table prefixes from column names
    for table in data:
        data[table].columns = [col.split('.')[-1] for col in data[table].columns]

    # Visualize avg_temp_by_prov_month
    if 'prov' in data['avg_temp_by_prov_month'].columns:
        plt.figure(figsize=(10, 6))
        for prov in data['avg_temp_by_prov_month']['prov'].unique():
            prov_data = data['avg_temp_by_prov_month'][data['avg_temp_by_prov_month']['prov'] == prov]
            plt.plot(prov_data['month'], prov_data['avg_temp'], label=prov)
        plt.xlabel('Month')
        plt.ylabel('Average Temperature')
        plt.title('Average Temperature by Province and Month')
        plt.legend()
        avg_temp_path = os.path.join(results_path, 'avg_temp_by_prov_month.png')
        plt.savefig(avg_temp_path)
        logger.info(f"Saved avg_temp_by_prov_month.png to {avg_temp_path}")
    else:
        logger.error("Column 'prov' not found in avg_temp_by_prov_month")

    # Visualize seasonal_trends_by_prov
    if 'prov' in data['seasonal_trends_by_prov'].columns:
        plt.figure(figsize=(10, 6))
        for prov in data['seasonal_trends_by_prov']['prov'].unique():
            prov_data = data['seasonal_trends_by_prov'][data['seasonal_trends_by_prov']['prov'] == prov]
            plt.plot(prov_data['season'], prov_data['avg_temp'], label=f'{prov} - Temp')
            plt.plot(prov_data['season'], prov_data['avg_wind_speed'], label=f'{prov} - Wind Speed')
        plt.xlabel('Season')
        plt.ylabel('Values')
        plt.title('Seasonal Trends by Province')
        plt.legend()
        seasonal_trends_path = os.path.join(results_path, 'seasonal_trends_by_prov.png')
        plt.savefig(seasonal_trends_path)
        logger.info(f"Saved seasonal_trends_by_prov.png to {seasonal_trends_path}")
    else:
        logger.error("Column 'prov' not found in seasonal_trends_by_prov")

    # Visualize temp_humidity_correlation_by_prov_month
    if 'prov' in data['temp_humidity_correlation_by_prov_month'].columns:
        plt.figure(figsize=(10, 6))
        for prov in data['temp_humidity_correlation_by_prov_month']['prov'].unique():
            prov_data = data['temp_humidity_correlation_by_prov_month'][
                data['temp_humidity_correlation_by_prov_month']['prov'] == prov]
            plt.plot(prov_data['month'], prov_data['correlation'], label=prov)
        plt.xlabel('Month')
        plt.ylabel('Correlation')
        plt.title('Temperature-Humidity Correlation by Province and Month')
        plt.legend()
        temp_humidity_path = os.path.join(results_path, 'temp_humidity_correlation_by_prov_month.png')
        plt.savefig(temp_humidity_path)
        logger.info(f"Saved temp_humidity_correlation_by_prov_month.png to {temp_humidity_path}")
    else:
        logger.error("Column 'prov' not found in temp_humidity_correlation_by_prov_month")

    logger.info("Visualizations created and saved successfully.")


if __name__ == "__main__":
    create_visualizations()
