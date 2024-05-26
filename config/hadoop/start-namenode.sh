#!/bin/bash

# Start SSH service
service ssh start

# Start Hadoop NameNode
$HADOOP_HOME/sbin/hadoop-daemon.sh start namenode

# Keep the container running
tail -f /dev/null