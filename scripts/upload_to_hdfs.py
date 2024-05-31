import os
from hdfs import InsecureClient

# HDFS configuration
hdfs_host = 'http://namenode:9870'
hdfs_user = 'root'
hdfs_client = InsecureClient(hdfs_host, user=hdfs_user)


def upload_files_to_hdfs():
    # Local directory containing CSV files
    local_dir = '/opt/airflow/dataset'
    # HDFS directory where files will be uploaded
    hdfs_dir = '/data/raw'

    # List of files to upload
    files = ['central_west.csv', 'north.csv', 'northeast.csv', 'south.csv', 'southeast.csv']

    for file in files:
        local_path = os.path.join(local_dir, file)
        hdfs_path = os.path.join(hdfs_dir, file)
        with open(local_path, 'rb') as f:
            hdfs_client.write(hdfs_path, f, overwrite=True)
        print(f"Uploaded {local_path} to {hdfs_path}")


if __name__ == "__main__":
    upload_files_to_hdfs()
