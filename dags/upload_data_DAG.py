from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

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
    'upload_to_hdfs',
    default_args=default_args,
    description='Convert CSV to Parquet and upload to HDFS',
    schedule_interval=timedelta(days=1),
)


def upload_files():
    import sys
    sys.path.append('/usr/local/airflow/scripts')
    from scripts.upload_data import upload_files_to_hdfs
    upload_files_to_hdfs()


t1 = PythonOperator(
    task_id='upload_files_to_hdfs',
    python_callable=upload_files,
    dag=dag,
)

t1
