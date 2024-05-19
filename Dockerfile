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

# Configure SSH
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys && \
    echo "Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile=/dev/null" > ~/.ssh/config

# Copy Hadoop configuration files (these should be prepared based on your setup)
COPY core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
COPY hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml
COPY mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml
COPY yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml

# Format HDFS namenode
RUN $HADOOP_HOME/bin/hdfs namenode -format

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]