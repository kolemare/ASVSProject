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
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'hive_visualization_dag',
    default_args=default_args,
    description='Fetch data from Hive and create visualizations',
    schedule_interval=None,
)


def run_visualization_script():
    from hive_visualization import create_visualizations
    create_visualizations()


create_visualizations_task = PythonOperator(
    task_id='create_visualizations',
    python_callable=run_visualization_script,
    dag=dag,
)

create_visualizations_task
