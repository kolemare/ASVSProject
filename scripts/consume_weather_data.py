import json
import time
import signal
import sys
from kafka import KafkaConsumer
from pyhive import hive
import pandas as pd
from datetime import datetime
import unicodedata

# Kafka configuration
KAFKA_TOPIC = 'weather_data'
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'

# Hive configuration
HIVE_HOST = 'hive-server2'
HIVE_PORT = 10000
HIVE_DATABASE = 'default'  # Adjust if needed

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

REALTIME_BATCH = config.get("realtime_batch", 50)  # Default to 50 if not specified


# Normalize city names to avoid discrepancies
def normalize_city_name(city_name):
    return unicodedata.normalize('NFKD', city_name).encode('ASCII', 'ignore').decode('ASCII').lower()


# Initialize the Hive connection
def create_hive_connection(retry_delay=5):
    try_num = 1
    while True:
        try:
            print(f"Connecting to Hive on {HIVE_HOST}:{HIVE_PORT}, database: {HIVE_DATABASE} (attempt {try_num})",
                  flush=True)
            return hive.Connection(host=HIVE_HOST, port=HIVE_PORT, username='hive', database=HIVE_DATABASE)
        except Exception as e:
            print(f"Failed to connect to Hive (attempt {try_num}): {e}", flush=True)
            time.sleep(retry_delay)
            try_num += 1


# Execute a Hive query
def execute_hive_query(query):
    conn = create_hive_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
    except Exception as e:
        print(f"Failed to execute Hive query: {e}", flush=True)
    finally:
        conn.close()


# Create the results table in Hive if it doesn't exist
def create_results_table():
    query = """
    CREATE TABLE IF NOT EXISTS weather_data_accumulated (
        city STRING,
        country STRING,
        coord_lon DOUBLE,
        coord_lat DOUBLE,
        weather_id INT,
        weather_main STRING,
        weather_description STRING,
        weather_icon STRING,
        base STRING,
        main_temp DOUBLE,
        main_feels_like DOUBLE,
        main_temp_min DOUBLE,
        main_temp_max DOUBLE,
        main_pressure INT,
        main_humidity INT,
        main_sea_level DOUBLE,
        main_grnd_level DOUBLE,
        visibility INT,
        wind_speed DOUBLE,
        wind_deg INT,
        wind_gust DOUBLE,
        rain_1h DOUBLE,
        clouds_all INT,
        dt INT,
        sys_type INT,
        sys_id INT,
        sys_sunrise INT,
        sys_sunset INT,
        timezone INT,
        cod INT
    )
    STORED AS PARQUET
    LOCATION '/data/results/weather_data_accumulated'
    """
    execute_hive_query(query)


# Create the transformed data table in Hive if it doesn't exist
def create_transformed_table():
    query = """
    CREATE TABLE IF NOT EXISTS weather_processed_stream_data (
        city STRING,
        country STRING,
        dt INT,
        thi DOUBLE,
        wci DOUBLE,
        hi DOUBLE,
        dew_point DOUBLE,
        visibility_ratio DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/data/results/weather_processed_stream_data'
    """
    execute_hive_query(query)


# Kafka consumer with retry logic
def create_kafka_consumer(topic, bootstrap_servers, max_retries=5, retry_delay=5):
    attempt = 0
    while True:
        try:
            print(f"Connecting to Kafka on {bootstrap_servers}, topic: {topic} (attempt {attempt + 1})", flush=True)
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            print("Connected to Kafka", flush=True)
            return consumer
        except Exception as e:
            print(f"Failed to connect to Kafka (attempt {attempt + 1}): {e}", flush=True)
            time.sleep(retry_delay)
            attempt += 1


# Calculate Temperature-Humidity Index (THI)
def calculate_thi(temperature_celsius, humidity):
    return temperature_celsius - ((0.55 - (0.55 * humidity / 100)) * (temperature_celsius - 58))


# Calculate Wind Chill Index (WCI)
def calculate_wci(temperature_celsius, wind_speed_kmh):
    wind_speed_mph = wind_speed_kmh * 0.621371
    return 35.74 + 0.6215 * temperature_celsius - 35.75 * (wind_speed_mph ** 0.16) + 0.4275 * temperature_celsius * (
                wind_speed_mph ** 0.16)


# Calculate Heat Index (HI)
def calculate_hi(temperature_fahrenheit, humidity):
    return -42.379 + 2.04901523 * temperature_fahrenheit + 10.14333127 * humidity - 0.22475541 * temperature_fahrenheit * humidity \
        - 0.00683783 * temperature_fahrenheit ** 2 - 0.05481717 * humidity ** 2 + 0.00122874 * temperature_fahrenheit ** 2 * humidity \
        + 0.00085282 * temperature_fahrenheit * humidity ** 2 - 0.00000199 * temperature_fahrenheit ** 2 * humidity ** 2


# Calculate Dew Point
def calculate_dew_point(temperature_celsius, humidity):
    a = 17.27
    b = 237.7
    alpha = ((a * temperature_celsius) / (b + temperature_celsius)) + (humidity / 100.0)
    return (b * alpha) / (a - alpha)


# Calculate Visibility Ratio
def calculate_visibility_ratio(visibility, max_visibility=10000):
    return visibility / max_visibility if visibility is not None else None


# Graceful shutdown
def signal_handler(sig, frame):
    print("Gracefully shutting down...", flush=True)
    consumer.close()
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def process_accumulated_data():
    # Retrieve data from accumulated table
    query = "SELECT * FROM weather_data_accumulated"
    conn = create_hive_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print("No data in accumulated table.", flush=True)
        return

    # Debug: Print column names and head of dataframe
    print("Accumulated DataFrame columns:", df.columns, flush=True)
    print("Accumulated DataFrame head:", df.head(), flush=True)

    # Rename columns to remove the table prefix
    df.columns = [col.split('.')[-1] for col in df.columns]

    cities = df['city'].apply(normalize_city_name).unique()
    for city in cities:
        city_df = df[df['city'].apply(normalize_city_name) == city]

        # Calculate required transformations
        avg_temp = city_df['main_temp'].mean()
        thi = calculate_thi(city_df['main_temp'].mean(), city_df['main_humidity'].mean())
        wci = calculate_wci(city_df['main_temp'].mean(), city_df['wind_speed'].mean())
        hi = calculate_hi(city_df['main_temp'].mean(), city_df['main_humidity'].mean())
        dew_point = calculate_dew_point(city_df['main_temp'].mean(), city_df['main_humidity'].mean())
        visibility_ratio = calculate_visibility_ratio(city_df['visibility'].mean())

        # Prepare the result to insert into Hive
        result = {
            'city': city_df['city'].iloc[0],
            'country': city_df['country'].iloc[0],
            'dt': int(city_df['dt'].mean()),
            'thi': thi,
            'wci': wci,
            'hi': hi,
            'dew_point': dew_point,
            'visibility_ratio': visibility_ratio
        }

        # Insert result into Hive
        insert_query = f"""
        INSERT INTO weather_processed_stream_data VALUES (
            '{result['city']}',
            '{result['country']}',
            {result['dt']},
            {result['thi']},
            {result['wci']},
            {result['hi']},
            {result['dew_point']},
            {result['visibility_ratio']}
        )
        """
        execute_hive_query(insert_query)


def process_stream_data():
    message_counter = 0  # Initialize message counter

    for message in consumer:
        weather_data = message.value

        # Extract data from API response
        city = weather_data['name']
        city = normalize_city_name(city)  # Normalize city name
        print(city, flush=True)
        country = weather_data['sys']['country']
        coord_lon = weather_data['coord']['lon']
        coord_lat = weather_data['coord']['lat']
        weather_id = weather_data['weather'][0]['id']
        weather_main = weather_data['weather'][0]['main']
        weather_description = weather_data['weather'][0]['description']
        weather_icon = weather_data['weather'][0]['icon']
        base = weather_data['base']
        main_temp = weather_data['main']['temp']
        main_feels_like = weather_data['main']['feels_like']
        main_temp_min = weather_data['main']['temp_min']
        main_temp_max = weather_data['main']['temp_max']
        main_pressure = weather_data['main']['pressure']
        main_humidity = weather_data['main']['humidity']
        main_sea_level = weather_data['main'].get('sea_level', None)
        main_grnd_level = weather_data['main'].get('grnd_level', None)
        visibility = weather_data.get('visibility', None)
        wind_speed = weather_data['wind']['speed']
        wind_deg = weather_data['wind']['deg']
        wind_gust = weather_data['wind'].get('gust', None)
        rain_1h = weather_data['rain']['1h'] if 'rain' in weather_data else None
        clouds_all = weather_data['clouds']['all']
        dt = weather_data['dt']
        sys_type = weather_data['sys'].get('type', None)
        sys_id = weather_data['sys'].get('id', None)
        sys_sunrise = weather_data['sys']['sunrise']
        sys_sunset = weather_data['sys']['sunset']
        timezone = weather_data['timezone']
        cod = weather_data['cod']

        # Add transformations
        transformed_data = {
            'city': city,
            'country': country,
            'coord_lon': coord_lon,
            'coord_lat': coord_lat,
            'weather_id': weather_id,
            'weather_main': weather_main,
            'weather_description': weather_description,
            'weather_icon': weather_icon,
            'base': base,
            'main_temp': main_temp,
            'main_feels_like': main_feels_like,
            'main_temp_min': main_temp_min,
            'main_temp_max': main_temp_max,
            'main_pressure': main_pressure,
            'main_humidity': main_humidity,
            'main_sea_level': main_sea_level,
            'main_grnd_level': main_grnd_level,
            'visibility': visibility,
            'wind_speed': wind_speed,
            'wind_deg': wind_deg,
            'wind_gust': wind_gust,
            'rain_1h': rain_1h,
            'clouds_all': clouds_all,
            'dt': dt,
            'sys_type': sys_type,
            'sys_id': sys_id,
            'sys_sunrise': sys_sunrise,
            'sys_sunset': sys_sunset,
            'timezone': timezone,
            'cod': cod
        }

        # Insert raw data into Hive
        insert_raw_query = f"""
        INSERT INTO weather_data_accumulated VALUES (
            '{city}',
            '{country}',
            {coord_lon},
            {coord_lat},
            {weather_id},
            '{weather_main}',
            '{weather_description}',
            '{weather_icon}',
            '{base}',
            {main_temp},
            {main_feels_like},
            {main_temp_min},
            {main_temp_max},
            {main_pressure},
            {main_humidity},
            {main_sea_level if pd.notna(main_sea_level) else 'NULL'},
            {main_grnd_level if pd.notna(main_grnd_level) else 'NULL'},
            {visibility if pd.notna(visibility) else 'NULL'},
            {wind_speed},
            {wind_deg},
            {wind_gust if pd.notna(wind_gust) else 'NULL'},
            {rain_1h if pd.notna(rain_1h) else 'NULL'},
            {clouds_all},
            {dt},
            {sys_type if pd.notna(sys_type) else 'NULL'},
            {sys_id if pd.notna(sys_id) else 'NULL'},
            {sys_sunrise},
            {sys_sunset},
            {timezone},
            {cod}
        )
        """
        execute_hive_query(insert_raw_query)

        message_counter += 1  # Increment the counter

        if message_counter >= REALTIME_BATCH:
            process_accumulated_data()  # Process accumulated data after reaching the batch size
            message_counter = 0  # Reset the counter


if __name__ == "__main__":
    create_results_table()
    create_transformed_table()
    consumer = create_kafka_consumer(KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS)
    process_stream_data()
