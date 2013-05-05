__author__ = 'Rod'

import sensordatastore
import datasinkstore
import time
import mysql.connector
import datetime
import lcd

print("Starting up..")


display = lcd.LCD()

sensor_ds = sensordatastore.SensorDataStore()
sensors = sensor_ds.get_sensors()

sink_ds = datasinkstore.DataSinkStore()
sinks = sink_ds.get_sinks()


errors_occured = 0

display.set_backlight(True)

while True:
    # read out the current data points
    current_time = datetime.datetime.utcnow()

    temp = None
    humidity = None
    movement = None

    for sensor in sensors:
        try:
            points_to_upload = sensor.get_datapoints()
        except Exception:
            errors_occured += 1
            print "Error reading from sensor.  id="+str(sensor.id)+" skipping read"
            continue
        for key, value in points_to_upload.items():
            if key == 'tempc':
                temp = value
            elif key == 'hum':
                humidity = value
            elif key == 'movement':
                movement = value
            print("# " + str(key) + " = " + str(value))
        for sink in sinks:
            try:
                sink.upload_datapoints(current_time, sensor, points_to_upload)
            except:
                errors_occured += 1
                print "Error writing to stream.  moving on"

    display.clear()
    display.write_text(str(humidity) + "% " + str(temp) + "C M"+str(movement)+" ")
    display.set_row_number(1)
    display.write_text('Errors: ' + str(errors_occured) + "  ")

    time.sleep(10)


