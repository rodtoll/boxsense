__author__ = 'Rod'

import sensordatastore
import datasinkstore
import time
import datetime
import lcd
import socket

def get_local_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    result = s.getsockname()[0]
    s.close()
    return result

print("Starting up..")


display = lcd.LCD()

sensor_ds = sensordatastore.SensorDataStore()
sensors = sensor_ds.get_sensors()

sink_ds = datasinkstore.DataSinkStore()
sinks = sink_ds.get_sinks()


address = get_local_address()

errors_occured = 0

display.set_backlight(True)

lcd_mode = True

temp = None
humidity = None
movement = None
light_level = None

main_screen = True

while True:
    # read out the current data points
    current_time = datetime.datetime.utcnow()

    any_change = False

    for sensor in sensors:

        if sensor.is_data_ready(current_time):
            try:
                points_to_upload = sensor.get_datapoints()
            except Exception:
                errors_occured += 1
                print "Error reading from sensor.  id="+str(sensor.id)+" skipping read"
                continue

            for key, value in points_to_upload.items():
                if key == 'tempc':
                    any_change = True
                    if value is not None:
                        temp = value
                elif key == 'hum':
                    any_change = True
                    if value is not None:
                        humidity = value
                elif key == 'movement':
                    any_change = True
                    movement = value
                elif key == 'light_level':
                    any_change = True
                    light_level = value
                elif key == 'button_press':
                    any_change = True
                    if value == 1:
                        main_screen = not main_screen

                print("# " + str(key) + " = " + str(value))

            for sink in sinks:
                try:
                    sink.upload_datapoints(current_time, sensor, points_to_upload)
                except:
                    errors_occured += 1
                    print "Error writing to stream.  moving on"

    if any_change:
        display.clear()
        if main_screen:
            display.write_text(str(humidity) + "% " + str(temp) + "C M"+str(movement)+" ")
            display.set_row_number(1)
            display.write_text("LL " + str(light_level))
        else:
            display.write_text('Errors: ' + str(errors_occured) + "  ")
            display.set_row_number(1)
            display.write_text(address)

    time.sleep(0.1)


