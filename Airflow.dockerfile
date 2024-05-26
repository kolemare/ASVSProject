# Use the official Airflow image as the base
FROM apache/airflow:2.9.1

# Switch to root user to install additional packages
USER airflow

# Install the hdfs package and any other dependencies
RUN pip install hdfs