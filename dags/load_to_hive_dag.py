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
    'load_to_hive',
    default_args=default_args,
    description='Load Parquet files from HDFS into Hive (Curated Zone)',
    schedule_interval=None,
)

def create_hive_table_task():
    from load_to_hive import create_hive_table
    create_hive_table()

def load_data_to_hive_task():
    from load_to_hive import load_data_to_hive
    load_data_to_hive()

create_table_task = PythonOperator(
    task_id='create_hive_table',
    python_callable=create_hive_table_task,
    dag=dag,
)

load_data_task = PythonOperator(
    task_id='load_data_to_hive',
    python_callable=load_data_to_hive_task,
    dag=dag,
)

trigger_avg_temp_dag = TriggerDagRunOperator(
    task_id='trigger_calculate_avg_temp_dag',
    trigger_dag_id='calculate_avg_temp_dag',
    dag=dag,
)

create_table_task >> load_data_task >> trigger_avg_temp_dag
