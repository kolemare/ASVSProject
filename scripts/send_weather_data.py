# scripts/send_weather_data.py

import json
import time
import requests
from kafka import KafkaProducer
import logging

# Kafka configuration
KAFKA_TOPIC = 'weather_data'
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'

# Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_weather_data(city, REQUEST_URL, API_KEY):
    try:
        response = requests.get(f"{REQUEST_URL}q={city}&appid={API_KEY}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch weather data for {city}: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error occurred: {e}")
        return None


def send_weather_data_to_kafka(url=None, city_province_mapping=None, apikey=None):
    if city_province_mapping is not None and url is not None and apikey is not None:
        for region in city_province_mapping:
            for cities in region.values():
                for city_info in cities:
                    city = city_info['city']
                    weather_data = fetch_weather_data(city, url, apikey)
                    if weather_data:
                        producer.send(KAFKA_TOPIC, weather_data)
                        logger.info(f"Sent weather data for {city} to Kafka")
                    time.sleep(1)  # Delay between requests
    else:
        logger.error("Missing configuration parameters")


if __name__ == "__main__":
    send_weather_data_to_kafka()
