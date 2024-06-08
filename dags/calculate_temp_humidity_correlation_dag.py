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
    'start_date': datetime(2023, 1, 1),  # Adjust as necessary
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'calculate_temp_humidity_correlation_dag',
    default_args=default_args,
    description='Calculate Correlation between Temperature and Humidity by Province and Month',
    schedule_interval=None,
)


def create_temp_humidity_correlation_table_task():
    from calculate_temp_humidity_correlation import create_temp_humidity_correlation_table
    create_temp_humidity_correlation_table()


def insert_temp_humidity_correlation_data_task():
    from calculate_temp_humidity_correlation import insert_temp_humidity_correlation_data
    insert_temp_humidity_correlation_data()


create_table_task = PythonOperator(
    task_id='create_temp_humidity_correlation_table',
    python_callable=create_temp_humidity_correlation_table_task,
    dag=dag,
)

insert_data_task = PythonOperator(
    task_id='insert_temp_humidity_correlation_data',
    python_callable=insert_temp_humidity_correlation_data_task,
    dag=dag,
)

create_table_task >> insert_data_task
