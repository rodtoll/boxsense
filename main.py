__author__ = 'Rod'

import DataSink
import Sensors
import time



sqlfeedconfig_json = '{"database_name": "test", "table_name": "sensor_readings", "field_map": {"tempc": 1, "hum": 2, "movement": 3}}'

motion_sensor_json = '{"pin_id":18, "no_movement_timeout_s": 6, "result_name":"movement"}'

sqlfeed = DataSink.datasink_create(1, sqlfeedconfig_json)
feed = DataSink.datasink_create(2, config_json)
feed_isy = DataSink.datasink_create(3, isyfeedconfig_json)

sensor = Sensors.sensor_create(2, 1, sensor_json)
sensor2 = Sensors.sensor_create(1, 2, motion_sensor_json)

while True:
    points = sensor.get_datapoints()
    points.update(sensor2.get_datapoints())

    for key, value in points.items():
        print("Key:" +str(key) + "Value: " + str(value))

    feed.upload_datapoints(sensor, points)
    feed_isy.upload_datapoints(sensor, points)
    sqlfeed.upload_datapoints(sensor, points)

    time.sleep(3)


