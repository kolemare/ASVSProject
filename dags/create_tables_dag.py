from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import os
import sys

# Add the scripts directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'create_tables_dag',
    default_args=default_args,
    description='Create all necessary tables for batch processing',
    schedule_interval=None,
)


def create_avg_temp_table_task():
    from create_tables import create_avg_temp_table
    create_avg_temp_table()


def create_seasonal_trends_table_task():
    from create_tables import create_seasonal_trends_table
    create_seasonal_trends_table()


def create_temp_humidity_correlation_table_task():
    from create_tables import create_temp_humidity_correlation_table
    create_temp_humidity_correlation_table()


# New table creation tasks
def create_thermal_humidity_index_table_task():
    from create_tables import create_thermal_humidity_index_table
    create_thermal_humidity_index_table()


def create_wind_direction_distribution_table_task():
    from create_tables import create_wind_direction_distribution_table
    create_wind_direction_distribution_table()


def create_pressure_extremes_table_task():
    from create_tables import create_pressure_extremes_table
    create_pressure_extremes_table()


def create_temp_variability_table_task():
    from create_tables import create_temp_variability_table
    create_temp_variability_table()


def create_solar_radiation_table_task():
    from create_tables import create_solar_radiation_table
    create_solar_radiation_table()


def create_avg_dew_point_table_task():
    from create_tables import create_avg_dew_point_table
    create_avg_dew_point_table()


def create_avg_wind_speed_table_task():
    from create_tables import create_avg_wind_speed_table
    create_avg_wind_speed_table()


# Task Definitions
create_avg_temp_table = PythonOperator(
    task_id='create_avg_temp_table',
    python_callable=create_avg_temp_table_task,
    dag=dag,
)

create_seasonal_trends_table = PythonOperator(
    task_id='create_seasonal_trends_table',
    python_callable=create_seasonal_trends_table_task,
    dag=dag,
)

create_temp_humidity_correlation_table = PythonOperator(
    task_id='create_temp_humidity_correlation_table',
    python_callable=create_temp_humidity_correlation_table_task,
    dag=dag,
)

create_thermal_humidity_index_table = PythonOperator(
    task_id='create_thermal_humidity_index_table',
    python_callable=create_thermal_humidity_index_table_task,
    dag=dag,
)

create_wind_direction_distribution_table = PythonOperator(
    task_id='create_wind_direction_distribution_table',
    python_callable=create_wind_direction_distribution_table_task,
    dag=dag,
)

create_pressure_extremes_table = PythonOperator(
    task_id='create_pressure_extremes_table',
    python_callable=create_pressure_extremes_table_task,
    dag=dag,
)

create_temp_variability_table = PythonOperator(
    task_id='create_temp_variability_table',
    python_callable=create_temp_variability_table_task,
    dag=dag,
)

create_solar_radiation_table = PythonOperator(
    task_id='create_solar_radiation_table',
    python_callable=create_solar_radiation_table_task,
    dag=dag,
)

create_avg_dew_point_table = PythonOperator(
    task_id='create_avg_dew_point_table',
    python_callable=create_avg_dew_point_table_task,
    dag=dag,
)

create_avg_wind_speed_table = PythonOperator(
    task_id='create_avg_wind_speed_table',
    python_callable=create_avg_wind_speed_table_task,
    dag=dag,
)

trigger_batch_processing_dag = TriggerDagRunOperator(
    task_id='trigger_batch_processing_dag',
    trigger_dag_id='batch_processing_dag',
    dag=dag,
)

# Define Task Order
create_avg_temp_table >> create_seasonal_trends_table >> create_temp_humidity_correlation_table
create_temp_humidity_correlation_table >> create_thermal_humidity_index_table >> create_wind_direction_distribution_table
create_wind_direction_distribution_table >> create_pressure_extremes_table >> create_temp_variability_table
create_temp_variability_table >> create_solar_radiation_table >> create_avg_dew_point_table
create_avg_dew_point_table >> create_avg_wind_speed_table >> trigger_batch_processing_dag
