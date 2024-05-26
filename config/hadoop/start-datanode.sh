#!/bin/bash

# Start SSH service
service ssh start

# Start Hadoop DataNode
$HADOOP_HOME/sbin/hadoop-daemon.sh start datanode

# Keep the container running
tail -f /dev/null