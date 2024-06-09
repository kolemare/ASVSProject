import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import os
import sys

# Add the scripts directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

# Load configuration
with open(os.path.join(os.path.dirname(__file__), 'config.json')) as config_file:
    config = json.load(config_file)
batches = config.get("batches", 3)

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
    'batch_processing_dag',
    default_args=default_args,
    description='Batch Processing with Configurable Batch Size',
    schedule_interval=None,
)


def process_batch(batch_index):
    from process_batch import process_data_for_batch
    process_data_for_batch(batch_index, batches)


for batch_index in range(batches):
    process_task = PythonOperator(
        task_id=f'process_batch_{batch_index}',
        python_callable=process_batch,
        op_args=[batch_index],
        dag=dag,
    )
    if batch_index > 0:
        prev_task = dag.get_task(f'process_batch_{batch_index - 1}')
        prev_task >> process_task

# Trigger the aggregation DAG after completing all batch processing
trigger_aggregation_dag = TriggerDagRunOperator(
    task_id='trigger_aggregation_dag',
    trigger_dag_id='aggregate_results_dag',
    dag=dag,
)

process_task >> trigger_aggregation_dag
