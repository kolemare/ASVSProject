from airflow import DAG
from airflow.operators.python_operator import PythonOperator
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
    'upload_sample_file_to_hdfs',
    default_args=default_args,
    description='Upload a sample text file to HDFS',
    schedule_interval=None,
)


def upload_sample_file():
    import sys
    sys.path.append('/usr/local/airflow/scripts')
    from upload_sample import upload_sample_to_hdfs
    upload_sample_to_hdfs()


t1 = PythonOperator(
    task_id='upload_sample_to_hdfs',
    python_callable=upload_sample_file,
    dag=dag,
)

t1
