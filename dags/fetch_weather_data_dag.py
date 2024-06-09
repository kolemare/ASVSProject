# dags/fetch_weather_data_dag.py

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import os
import sys
import json

# Add the scripts directory to the Python path
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../scripts')
sys.path.append(SCRIPT_PATH)

# Load configuration
with open(os.path.join(os.path.dirname(__file__), 'config.json')) as f:
    config = json.load(f)
    url = config.get("request_url")
    city_province_mapping = config.get("city_province_mapping")

with open(os.path.join(os.path.dirname(__file__), 'apikey.json')) as f:
    apikey = json.load(f)
    apikey = apikey.get("key")

batches = config.get("batches", 3)

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
    'fetch_weather_data_dag',
    default_args=default_args,
    description='Fetch weather data and send to Kafka',
    schedule_interval=None,  # No fixed interval
    catchup=False,
)


def fetch_weather_data():
    from send_weather_data import send_weather_data_to_kafka
    send_weather_data_to_kafka(url, city_province_mapping, apikey)


fetch_weather_data_task = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    dag=dag,
)

trigger_next_run = TriggerDagRunOperator(
    task_id='trigger_next_run',
    trigger_dag_id='fetch_weather_data_dag',  # Trigger the same DAG
    dag=dag,
)

fetch_weather_data_task >> trigger_next_run
