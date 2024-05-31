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
    'upload_to_hdfs',
    default_args=default_args,
    description='Upload CSV files to HDFS (Raw Zone)',
    schedule_interval=None,
)


def upload_files():
    from upload_to_hdfs import upload_files_to_hdfs
    upload_files_to_hdfs()


t1 = PythonOperator(
    task_id='upload_files_to_hdfs',
    python_callable=upload_files,
    dag=dag,
)

t2 = TriggerDagRunOperator(
    task_id='trigger_transform_to_parquet_dag',
    trigger_dag_id='transform_to_parquet',
    dag=dag,
)

t1 >> t2
