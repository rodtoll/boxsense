__author__ = 'Rod'

import json
import subprocess
import time
import re


class Sensor:
    def __init__(self, json_config):
        self.config = self.json_to_config(json_config)

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
    def __init(self, json_config):
        self.config = self.json_to_config(json_config)

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return ApplicationSensorConfig(fields['app_name'], fields['parameters'], fields['results'])

    def get_datapoints(self):
        print('Running command')
        params = list()
        params.append(self.config.app_name)
        params.extend(self.config.parameters)
        output = subprocess.check_output(params)
        print('Output: ')
        print(output)
        result = dict()
        for key, regex in self.config.results.items():
            matches = re.search(regex, output)
            if not matches:
                result[key] = None
            else:
                result[key] = float(matches.group(1))
        self.last_read = time.time()
        return result

def sensor_create(sensor_type, json_config):
    if sensor_type == 1:
        return None
    elif sensor_type == 2:
        return ApplicationSensor(json_config)
    else:
        print("Invalid sensor type specified: " + str(sensor_type))
        return None
