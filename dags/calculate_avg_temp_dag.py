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
    'calculate_avg_temp_dag',
    default_args=default_args,
    description='Calculate Average Temperature by Province and Month',
    schedule_interval=None,
)

def create_avg_temp_table_task():
    from calculate_avg_temp import create_avg_temp_table
    create_avg_temp_table()

def insert_avg_temp_data_task():
    from calculate_avg_temp import insert_avg_temp_data
    insert_avg_temp_data()

create_table_task = PythonOperator(
    task_id='create_avg_temp_table',
    python_callable=create_avg_temp_table_task,
    dag=dag,
)

insert_data_task = PythonOperator(
    task_id='insert_avg_temp_data',
    python_callable=insert_avg_temp_data_task,
    dag=dag,
)

trigger_seasonal_trends_dag = TriggerDagRunOperator(
    task_id='trigger_seasonal_trends_dag',
    trigger_dag_id='calculate_seasonal_trends_dag',  # The new DAG ID for seasonal trends
    dag=dag,
)

create_table_task >> insert_data_task >> trigger_seasonal_trends_dag
