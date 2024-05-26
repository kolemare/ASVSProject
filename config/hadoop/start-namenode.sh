#!/bin/bash

# Start SSH service
/usr/sbin/sshd

# Start Hadoop NameNode
$HADOOP_HOME/sbin/hadoop-daemon.sh start namenode

# Keep the container running
tail -f /dev/null