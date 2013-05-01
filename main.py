__author__ = 'Rod'

import DataFeed
import Sensors

sensor_stuff = Sensors.ApplicationSensorConfig('sudo',
                                  ['/home/pi/dht_driver/Adafruit-Raspberry-Pi-Python-Code/Adafruit_DHT_Driver/Adafruit_DHT', '22', '4'],
                                  ['Temp =\\s+([0-9.]+', 'Hum =\\s+([0-9.]+'])
sensor_stuff_json = sensor_stuff.get_json()

print("Hello world!")
print(sensor_stuff_json)

sensor_json = r'''{"app_name": "sudo", "parameters": ["/home/pi/dht_driver/Adafruit-Raspberry-Pi-Python-Code/Adafruit_DHT_Driver/Adafruit_DHT", "22", "4"], "results": {"tempc": "Temp =  ([0-9.]+)", "hum": "Hum = ([0-9.]+)"}}'''

config_json = '{"host": "api.cosm.com", "port": 80, "api_key": "VHEAxSvili9SEOUM-Z3_qUzb1baSAKxkZGJuZlBuOHBJUT0g", ' \
              '"feed_id": 127990, "feeds":{"hum": "humidity", "tempc":"temperature_c"}}'

feed = DataFeed.datafeed_create_feed(2, config_json)

sensor = Sensors.sensor_create(2, sensor_json)

points = sensor.get_datapoints()

for key, value in points.items():
    print("Key:" +str(key) + "Value: " + str(value))

feed.upload_datapoints(points)


