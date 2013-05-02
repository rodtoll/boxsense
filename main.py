__author__ = 'Rod'

import sensordatastore
import datasinkstore
import time
import mysql.connector

print("Starting up..")

connection = mysql.connector.connect(user='', password='', host='127.0.0.1', database='test')

sensor_ds = sensordatastore.SensorDataStore()
sensors = sensor_ds.get_sensors()

sink_ds = datasinkstore.DataSinkStore()
sinks = sink_ds.get_sinks()

while True:
    # read out the current data points
    for sensor in sensors:
        points_to_upload = sensor.get_datapoints()
        for sink in sinks:
            print("Feed: " + str(type(sink)))
            sink.upload_datapoints(sensor, points_to_upload)

    time.sleep(3)

