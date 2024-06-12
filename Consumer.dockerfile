FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libsasl2-dev \
    libsasl2-modules \
    libkrb5-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    && apt-get clean

# Install Python packages
RUN pip install --upgrade pip
RUN pip install kafka-python pandas pyhive thrift_sasl sqlalchemy

# Copy the consumer script
COPY scripts/consume_weather_data.py /app/consume_weather_data.py
COPY dags/config.json /app/config.json

# Set the working directory
WORKDIR /app

# Run the consumer script
CMD ["python", "consume_weather_data.py"]
