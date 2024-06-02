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

# Correct column names to match the Hive table schema
column_mapping = {
    'Data': 'date',
    'Hora': 'hour',
    'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'prcp',
    'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)': 'stp',
    'PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)': 'smax',
    'PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)': 'smin',
    'RADIACAO GLOBAL (Kj/m²)': 'gbrd',
    'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)': 'temp',
    'TEMPERATURA DO PONTO DE ORVALHO (°C)': 'dewp',
    'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)': 'tmax',
    'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)': 'tmin',
    'TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)': 'dmax',
    'TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)': 'dmin',
    'UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)': 'hmax',
    'UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)': 'hmin',
    'UMIDADE RELATIVA DO AR, HORARIA (%)': 'hmdy',
    'VENTO, DIREÇÃO HORARIA (gr) (° (gr))': 'wdct',
    'VENTO, RAJADA MAXIMA (m/s)': 'gust',
    'VENTO, VELOCIDADE HORARIA (m/s)': 'wdsp',
    'region': 'regi',
    'state': 'prov',
    'station': 'wsnm',
    'station_code': 'inme',
    'latitude': 'lat',
    'longitude': 'lon',
    'height': 'elvt'
}


def clean_data(df):
    for column in df.columns:
        df[column].replace(-9999, pd.NA, inplace=True)
    df.dropna(inplace=True)
    return df


def clean_and_rename_columns(df):
    df.rename(columns=column_mapping, inplace=True)
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
            df = clean_and_rename_columns(df)
            table = pa.Table.from_pandas(df)
            pq.write_table(table, parquet_file)
            hdfs_path = os.path.join(hdfs_dir, file.replace('.csv', '.parquet'))
            with open(parquet_file, 'rb') as f:
                hdfs_client.write(hdfs_path, f, overwrite=True)
            print(f"Uploaded transformed {raw_path} as {parquet_file} to {hdfs_path}")


if __name__ == "__main__":
    transform_and_upload_to_hdfs()
