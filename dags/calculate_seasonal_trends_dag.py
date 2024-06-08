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
    'calculate_seasonal_trends_dag',
    default_args=default_args,
    description='Calculate Seasonal Trends in Temperature and Wind Speed by Province',
    schedule_interval=None,
)


def create_seasonal_trends_table_task():
    from calculate_seasonal_trends import create_seasonal_trends_table
    create_seasonal_trends_table()


def insert_seasonal_trends_data_task():
    from calculate_seasonal_trends import insert_seasonal_trends_data
    insert_seasonal_trends_data()


create_table_task = PythonOperator(
    task_id='create_seasonal_trends_table',
    python_callable=create_seasonal_trends_table_task,
    dag=dag,
)

insert_data_task = PythonOperator(
    task_id='insert_seasonal_trends_data',
    python_callable=insert_seasonal_trends_data_task,
    dag=dag,
)

# Trigger the next DAG after completing the current one
trigger_next_dag = TriggerDagRunOperator(
    task_id='trigger_temp_humidity_correlation_dag',
    trigger_dag_id='calculate_temp_humidity_correlation_dag',  # Replace with the actual next DAG ID
    dag=dag,
)

create_table_task >> insert_data_task >> trigger_next_dag
