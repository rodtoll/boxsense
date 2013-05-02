__author__ = 'Rod'

import DataSink
import Sensors
import time
import mysql.connector

connection = mysql.connector.connect(user='', password='', host='127.0.0.1', database='test')

cursor = connection.cursor()
cursor.execute('SELECT * from sensors')
sensors = [Sensors.sensor_create(sensor_type, id, config) for id, sensor_type, config in cursor]
cursor.close()

cursor = connection.cursor()
cursor.execute('SELECT * from feeds')
feeds = [DataSink.datasink_create(feed_type, config) for id, feed_type, config in cursor]
cursor.close()


while True:

    # read out the current data points
    for sensor in sensors:
        points_to_upload = sensor.get_datapoints()
        for feed in feeds:
            print("Feed: " + str(type(feed)))
            feed.upload_datapoints(sensor, points_to_upload)

    time.sleep(3)

