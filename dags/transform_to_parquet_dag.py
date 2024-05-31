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
    'start_date': datetime(2023, 1, 1),  # A past date
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'transform_to_parquet',
    default_args=default_args,
    description='Transform CSV files to Parquet and upload to HDFS (Transformed Zone)',
    schedule_interval=None,
)


def transform_files():
    from transform_to_parquet import transform_and_upload_to_hdfs
    transform_and_upload_to_hdfs()


t1 = PythonOperator(
    task_id='transform_files_to_parquet',
    python_callable=transform_files,
    dag=dag,
)

t2 = TriggerDagRunOperator(
    task_id='trigger_load_to_hive_dag',
    trigger_dag_id='load_to_hive',
    dag=dag,
)

t1 >> t2
