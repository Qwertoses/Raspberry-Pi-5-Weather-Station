import time
import json
import requests
import board
import busio
from adafruit_bme280 import basic as bme280
import adafruit_sgp30
import digitalio

# --- Configuration ---
API_URL = "http://143.198.23.199/start_deployment.php"  # Change this!
SEND_INTERVAL = 5  # seconds between readings

# --- Sensor Setup ---
# Initialize I2C bus objects for sgp30
i2c_bus = busio.I2C(board.SCL, board.SDA, frequency=100000)
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c_bus)

# Initialize SPI bus object for bme280
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(board.D5)  # GPIO5
bme280 = bme280.Adafruit_BME280_SPI(spi, cs)

# Optional: set local sea-level pressure for accurate altitude
# bme280.sea_level_pressure = 1013.25

# Get Raspberry Pi Serial
def get_raspberry_pi_serial():
    """Retrieve the Raspberry Pi serial number from /proc/cpuinfo"""
    serial = "0000000000000000"  # Default serial as fallback
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    serial = line.strip().split(':')[1].strip()
                    break
    except Exception as e:
        serial = f"Error: {str(e)}"
    return serial

# Get the serial number
device_id = get_raspberry_pi_serial()

# Recieve Raspberry pi Deployment ID from Center
deployment_id = None


while deployment_id is None:
    try:
        response = requests.post(API_URL, json={"device_id": device_id}, timeout=5)
        response.raise_for_status()  # Raise error if bad response

        data = response.json()  # Parse JSON response

        # Assuming API returns something like: {"deployment_id": 3}
        deployment_id = data.get("deployment_id")

        if deployment_id is None:
            raise ValueError("deployment_id not found in API response")

        print(f"Received deployment_id: {deployment_id}")
    except requests.exceptions.Timeout:
        print("Request timed out. Retrying...")
    except Exception as e:
        print(f"Failed to get deployment ID: {e}")
    


API_URL = "http://143.198.23.199/ingest.php"  # Change this!
print("Weather station sender started. Sending to:", API_URL)


while True:
    try:
        # Read sensors
        temperature_f = bme280.temperature * 9 / 5 + 32
        humidity = bme280.relative_humidity
        pressure = bme280.pressure
        eco2, tvoc = sgp30.iaq_measure()

        # Build JSON payload
        payload = {
          "deployment_id": deployment_id, 
          "temp_f": round(temperature_f, 1),
          "humidity": round(humidity, 1),
          "pressure_hpa": round(pressure, 1),
          "eco2_ppm": eco2,
          "tvoc_ppb": tvoc
        }

       # Print locally
        print(f"\nDeployment_id: {deployment_id}")
        print(f"\nTemperature: {payload['temp_f']} °F")
        print(f"Humidity:    {payload['humidity']} %")
        print(f"Pressure:    {payload['pressure_hpa']} hPa")
        print(f"eCO2:        {payload['eco2_ppm']} ppm")
        print(f"TVOC:        {payload['tvoc_ppb']} ppb")

        # Send to API
        response = requests.post(API_URL, json=payload, timeout=5)
        print(f"-> Sent to API: {response.status_code}, {response.reason}")

    except requests.exceptions.RequestException as e:
        print(f"-> Failed to send: {e}")
    except Exception as e:
        print(f"Sensor error: {e}")

    time.sleep(SEND_INTERVAL)
