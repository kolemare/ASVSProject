import os
from hdfs import InsecureClient


def upload_sample_to_hdfs():
    # HDFS configuration
    hdfs_host = 'http://namenode:9870'
    hdfs_user = 'root'
    hdfs_client = InsecureClient(hdfs_host, user=hdfs_user)

    # Local and HDFS paths
    local_file_path = '/opt/airflow/dataset/sample.txt'
    hdfs_file_path = '/data/sample.txt'

    # Upload file to HDFS
    with open(local_file_path, 'rb') as f:
        hdfs_client.write(hdfs_file_path, f, overwrite=True)
    print(f"Uploaded {local_file_path} to {hdfs_file_path}")


if __name__ == "__main__":
    upload_sample_to_hdfs()
