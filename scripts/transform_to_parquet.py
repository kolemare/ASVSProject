import os
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from hdfs import InsecureClient
import tempfile

# HDFS configuration
hdfs_host = 'http://namenode:9870'
hdfs_user = 'root'
hdfs_client = InsecureClient(hdfs_host, user=hdfs_user)


def clean_data(df):
    for column in df.columns:
        df[column].replace(-9999, pd.NA, inplace=True)
    df.dropna(inplace=True)
    return df


def transform_and_upload_to_hdfs():
    # HDFS directory containing raw CSV files
    raw_dir = '/data/raw'
    # HDFS directory where transformed Parquet files will be uploaded
    hdfs_dir = '/data/transform'

    # List of files to transform
    files = ['central_west.csv', 'north.csv', 'northeast.csv', 'south.csv', 'southeast.csv']

    for file in files:
        raw_path = os.path.join(raw_dir, file)
        with tempfile.TemporaryDirectory() as temp_dir:
            parquet_file = os.path.join(temp_dir, file.replace('.csv', '.parquet'))
            with hdfs_client.read(raw_path) as f:
                df = pd.read_csv(f)
            df = clean_data(df)
            table = pa.Table.from_pandas(df)
            pq.write_table(table, parquet_file)
            hdfs_path = os.path.join(hdfs_dir, file.replace('.csv', '.parquet'))
            with open(parquet_file, 'rb') as f:
                hdfs_client.write(hdfs_path, f, overwrite=True)
            print(f"Uploaded transformed {raw_path} as {parquet_file} to {hdfs_path}")


if __name__ == "__main__":
    transform_and_upload_to_hdfs()
