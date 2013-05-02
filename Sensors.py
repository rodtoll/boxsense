__author__ = 'Rod'

import json
import subprocess
import time
import re
import RPi.GPIO as io

class Sensor:
    def __init__(self, id, json_config):
        self.config = self.json_to_config(json_config)
        self.id = id

    def get_datapoints(self, data_points):
        None

    def json_to_config(self, json_config):
        None

class ApplicationSensorConfig:
    def __init__(self, app_name, parameters, results):
        self.app_name = app_name
        self.parameters = parameters
        self.results = results

    def get_json(self):
        encoder = json.JSONEncoder()
        return encoder.encode(self.__dict__)

class ApplicationSensor(Sensor):
    def __init(self, id, json_config):
        Sensor.__init__(self, id, json_config)

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return ApplicationSensorConfig(fields['app_name'], fields['parameters'], fields['results'])

    def get_datapoints(self):
        params = list()
        params.append(self.config.app_name)
        params.extend(self.config.parameters)
        output = subprocess.check_output(params)
        result = dict()
        for key, regex in self.config.results.items():
            matches = re.search(regex, output)
            if not matches:
                result[key] = None
            else:
                result[key] = float(matches.group(1))
        self.last_read = time.time()
        return result

class MotionSensorConfig:
    def __init__(self, pin_id, no_movement_timeout_s, result_name):
        self.pin_id = pin_id
        self.no_movement_timeout_s = no_movement_timeout_s
        self.result_name = result_name

    def get_json(self):
        encoder = json.JSONEncoder()
        return encoder.encode(self.__dict__)

io.setmode(io.BCM)

class MotionSensor(Sensor):
    def __init__(self, id, json_config):
        Sensor.__init__(self, id, json_config)
        self.last_delta = time.time()
        io.setup(self.config.pin_id, io.IN)
        io.add_event_detect(self.config.pin_id, io.BOTH, bouncetime=200)
        print("Setting up sensor on pin: "+str(self.config.pin_id))
        io.add_event_callback(self.config.pin_id, self.motion_detected)

    def motion_detected(self, channel):
        print("State changed!")
        self.last_delta = time.time()

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return MotionSensorConfig(fields['pin_id'], fields['no_movement_timeout_s'], fields['result_name'])

    def get_datapoints(self):
        time_delta = time.time() - self.last_delta
        print("Delta is: "+str(time_delta))
        if time_delta < self.config.no_movement_timeout_s or time_delta <= 0:
            movement_detected = 1
        else:
            movement_detected = 0
        return { self.config.result_name: movement_detected }

def sensor_create(sensor_type, id, json_config):
    print("Creating sensor, for type: "+str(sensor_type))
    if sensor_type == 1:
        print("Creating GPIO")
        return MotionSensor(id, json_config)
    elif sensor_type == 2:
        print("Creating Application")
        return ApplicationSensor(id, json_config)
    else:
        print("Invalid sensor type specified: " + str(sensor_type))
        return None
