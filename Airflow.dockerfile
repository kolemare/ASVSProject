FROM apache/airflow:2.9.1
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-17-jre \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Switch back to airflow user
USER airflow

# Install Python packages
RUN pip install jaydebeapi pandas hdfs pyarrow

# Copy the JDBC driver
COPY --chown=airflow:root hive-jdbc-standalone.jar /opt/airflow/jdbc/hive-jdbc-standalone.jar
COPY --chown=airflow:root httpclient-4.5.13.jar /opt/airflow/jdbc/httpclient-4.5.13.jar
COPY --chown=airflow:root httpcore-4.4.13.jar /opt/airflow/jdbc/httpcore-4.4.13.jar

# Set the CLASSPATH environment variable
ENV CLASSPATH=/opt/airflow/jdbc/hive-jdbc-standalone.jar:/opt/airflow/jdbc/httpclient-4.5.13.jar:/opt/airflow/jdbc/httpcore-4.4.13.jar

