# Circuit Python bme280 and sgp30 implementation
import board
import time
import digitalio
import busio
import adafruit_sgp30
from adafruit_bme280 import basic as bme280

# Initialize I2C bus objects for sgp30
i2c_bus = busio.I2C(board.SCL, board.SDA, frequency=100000)
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c_bus)

# Initialize SPI bus object for bme280
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(board.D5)  # GPIO5
bme280 = bme280.Adafruit_BME280_SPI(spi, cs)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25

while True:
  print("\nTemperature: %0.1f F" % (bme280.temperature*9/5+32))
  print("Humidity: %0.1f %%" % bme280.relative_humidity)
  print("Pressure: %0.1f hPa" % bme280.pressure)
  print("Altitude = %0.2f meters" % bme280.altitude)
  eCO2, TVOC = sgp30.iaq_measure()
  print("eCO2 = %d ppm \t TVOC = %d ppb" % (eCO2, TVOC))
  time.sleep(2)
