import os
import pyarrow as pa
import pyarrow.parquet as pq
import csv
from hdfs import InsecureClient
import tempfile


def convert_csv_to_parquet(csv_file, parquet_file, columns, dtypes):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f, fieldnames=columns)
        rows = [row for row in reader]

    # Convert to Arrow table
    table = pa.Table.from_pylist(rows, schema=pa.schema(
        [(col, pa.from_numpy_dtype(dtype)) for col, dtype in zip(columns, dtypes.values())]))
    pq.write_table(table, parquet_file)


def upload_files_to_hdfs():
    # HDFS configuration
    hdfs_host = 'http://namenode:9870'
    hdfs_user = 'root'
    hdfs_client = InsecureClient(hdfs_host, user=hdfs_user)

    # Local directory containing CSV files
    local_dir = '/opt/airflow/dataset'
    # HDFS directory where files will be uploaded
    hdfs_dir = '/data/climate'

    # List of files to upload
    files = ['central_west.csv', 'north.csv', 'northeast.csv', 'south.csv', 'southeast.csv']
    columns = [
        'date', 'hour', 'prcp', 'stp', 'smax', 'smin', 'gbrd',
        'temp', 'dewp', 'tmax', 'tmin', 'dmax', 'dmin',
        'hmax', 'hmin', 'hmdy', 'wdct', 'gust', 'wdsp', 'regi',
        'prov', 'wsnm', 'inme', 'lat', 'lon', 'elvt'
    ]
    dtypes = {
        'date': str, 'hour': str, 'prcp': float, 'stp': float, 'smax': float,
        'smin': float, 'gbrd': float, 'temp': float, 'dewp': float, 'tmax': float,
        'tmin': float, 'dmax': float, 'dmin': float, 'hmax': float, 'hmin': float,
        'hmdy': float, 'wdct': float, 'gust': float, 'wdsp': float, 'regi': str,
        'prov': str, 'wsnm': str, 'inme': str, 'lat': float, 'lon': float, 'elvt': float
    }

    for file in files:
        local_path = os.path.join(local_dir, file)
        with tempfile.TemporaryDirectory() as temp_dir:
            parquet_file = os.path.join(temp_dir, file.replace('.csv', '.parquet'))
            convert_csv_to_parquet(local_path, parquet_file, columns, dtypes)
            hdfs_path = os.path.join(hdfs_dir, file.replace('.csv', '.parquet'))
            with open(parquet_file, 'rb') as f:
                hdfs_client.write(hdfs_path, f, overwrite=True)
            print(f"Uploaded {local_path} as {parquet_file} to {hdfs_path}")


if __name__ == "__main__":
    upload_files_to_hdfs()
