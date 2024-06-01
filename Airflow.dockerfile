FROM apache/airflow:2.9.1

# Switch to airflow user
USER airflow

# Install Python packages
RUN pip install pandas hdfs pyarrow apache-airflow-providers-apache-hive
