# Use an official Ubuntu as a parent image
FROM ubuntu:20.04

# Set environment variables
ENV HADOOP_VERSION=3.3.6
ENV HIVE_VERSION=4.0.0
ENV HBASE_VERSION=2.5.8
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HADOOP_HOME=/usr/local/hadoop
ENV HIVE_HOME=/usr/local/hive
ENV HBASE_HOME=/usr/local/hbase
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin:$HBASE_HOME/bin

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-8-jdk \
    ssh \
    rsync \
    curl \
    net-tools \
    netcat \
    && apt-get clean

# Download and extract Hadoop
RUN curl -O https://archive.apache.org/dist/hadoop/core/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzvf hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION /usr/local/hadoop && \
    rm hadoop-$HADOOP_VERSION.tar.gz

# Download and extract Hive
RUN curl -O https://archive.apache.org/dist/hive/hive-$HIVE_VERSION/apache-hive-$HIVE_VERSION-bin.tar.gz && \
    tar -xzvf apache-hive-$HIVE_VERSION-bin.tar.gz && \
    mv apache-hive-$HIVE_VERSION-bin /usr/local/hive && \
    rm apache-hive-$HIVE_VERSION-bin.tar.gz

# Download and extract HBase
RUN curl -O https://archive.apache.org/dist/hbase/$HBASE_VERSION/hbase-$HBASE_VERSION-bin.tar.gz && \
    tar -xzvf hbase-$HBASE_VERSION-bin.tar.gz && \
    mv hbase-$HBASE_VERSION /usr/local/hbase && \
    rm hbase-$HBASE_VERSION-bin.tar.gz

# Copy Hadoop, Hive, and HBase configuration files
COPY config/hadoop/core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
COPY config/hadoop/hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml
COPY config/hadoop/mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml
COPY config/hadoop/yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml
COPY config/hadoop/capacity-scheduler.xml $HADOOP_HOME/etc/hadoop/capacity-scheduler.xml
COPY config/hive/hive-site.xml $HIVE_HOME/conf/hive-site.xml
COPY config/hbase/hbase-site.xml $HBASE_HOME/conf/hbase-site.xml
COPY config/hbase/regionservers $HBASE_HOME/conf/regionservers
COPY config/hbase/hbase-env.sh $HBASE_HOME/conf/hbase-env.sh
COPY config/hadoop/start-namenode.sh /usr/local/bin/start-namenode.sh
COPY config/hadoop/start-datanode.sh /usr/local/bin/start-datanode.sh

# Add log4j.properties for HBase and Hadoop
COPY config/hadoop/log4j.properties $HADOOP_HOME/etc/hadoop/log4j.properties
COPY config/hbase/log4j.properties $HBASE_HOME/conf/log4j.properties

# Format HDFS namenode
RUN $HADOOP_HOME/bin/hdfs namenode -format

# Create necessary directory for SSH
RUN mkdir -p /run/sshd

# Configure SSH
RUN ssh-keygen -t rsa -P '' -f /root/.ssh/id_rsa && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 0600 /root/.ssh/authorized_keys && \
    echo "Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile=/dev/null" > /root/.ssh/config

# Start namenode and datanode scripts
RUN chmod +x /usr/local/bin/start-namenode.sh /usr/local/bin/start-datanode.sh

# Start SSH service and the NameNode or DataNode
CMD ["/usr/local/bin/start-namenode.sh"]