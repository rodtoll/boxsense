__author__ = 'Rod'

import json
import subprocess
import time
import re
import RPi.GPIO as io
import datetime

class Sensor:
    def __init__(self, id, json_config):
        self.config = self.json_to_config(json_config)
        self.id = id
        self.data_ready = False

    def get_datapoints(self, data_points):
        None

    def json_to_config(self, json_config):
        None

    def is_data_ready(self, current_time):
        return self.data_ready

class ApplicationSensorConfig:
    def __init__(self, app_name, parameters, results, minimum_delay):
        self.app_name = app_name
        self.parameters = parameters
        self.results = results
        self.minimum_delay = minimum_delay

    def get_json(self):
        encoder = json.JSONEncoder()
        return encoder.encode(self.__dict__)

class ApplicationSensor(Sensor):
    def __init__(self, id, json_config):
        Sensor.__init__(self, id, json_config)
        self.last_read = datetime.datetime.utcnow()

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return ApplicationSensorConfig(fields['app_name'], fields['parameters'], fields['results'], fields['minimum_delay'])

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
        self.last_read = datetime.datetime.utcnow()
        return result

    def is_data_ready(self, current_time):
        if (current_time - self.last_read).seconds > self.config.minimum_delay:
            return True
        else:
            return False

class AnalogSensorConfig:
    def __init__(self, spi_mosi_pin_id, spi_miso_pin_id, spi_clk_pin_id, spi_cs_pin_id, minimum_delay, pin_mapping):
        self.spi_mosi_pin_id = spi_mosi_pin_id
        self.spi_miso_pin_id = spi_miso_pin_id
        self.spi_clk_pin_id = spi_clk_pin_id
        self.spi_cs_pin_id = spi_cs_pin_id
        self.minimum_delay = minimum_delay
        self.pin_mapping = pin_mapping

    def get_json(self):
        encoder = json.JSONEncoder()
        return encoder.encode(self.__dict__)

class AnalogSensor(Sensor):
    def __init__(self, id, json_config):
        Sensor.__init__(self, id, json_config)
        io.setup(self.config.spi_mosi_pin_id, io.OUT)
        io.setup(self.config.spi_miso_pin_id, io.IN)
        io.setup(self.config.spi_clk_pin_id, io.OUT)
        io.setup(self.config.spi_cs_pin_id, io.OUT)
        self.last_read = datetime.datetime.utcnow()

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return AnalogSensorConfig(fields['spi_mosi_pin_id'], fields['spi_miso_pin_id'], fields['spi_clk_pin_id'], fields['spi_cs_pin_id'], fields['minimum_delay'], fields['pin_mapping'])

    def get_analog_pin_value(self, analog_pin_id):
        if ((analog_pin_id > 7) or (analog_pin_id < 0)):
                return -1
        io.output(self.config.spi_cs_pin_id, True)

        io.output(self.config.spi_clk_pin_id, False)  # start clock low
        io.output(self.config.spi_cs_pin_id, False)     # bring CS low

        commandout = analog_pin_id
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        io.output(self.config.spi_mosi_pin_id, True)
                else:
                        io.output(self.config.spi_mosi_pin_id, False)
                commandout <<= 1
                io.output(self.config.spi_clk_pin_id, True)
                io.output(self.config.spi_clk_pin_id, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                io.output(self.config.spi_clk_pin_id, True)
                io.output(self.config.spi_clk_pin_id, False)
                adcout <<= 1
                if (io.input(self.config.spi_miso_pin_id)):
                        adcout |= 0x1

        io.output(self.config.spi_cs_pin_id, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

    def get_datapoints(self):
        result = dict()
        for key, value in self.config.pin_mapping.items():
            result[key] = self.get_analog_pin_value(value)
        self.last_read = datetime.datetime.utcnow()
        return result

    def is_data_ready(self, current_time):
        if (current_time - self.last_read).seconds > self.config.minimum_delay:
            return True
        else:
            return False

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
        self.change_detected = True
        io.setup(self.config.pin_id, io.IN)
        io.add_event_detect(self.config.pin_id, io.BOTH, bouncetime=(self.config.no_movement_timeout_s*1000))
        print("Setting up sensor on pin: "+str(self.config.pin_id))
        io.add_event_callback(self.config.pin_id, self.motion_detected)

    def motion_detected(self, channel):
        self.change_detected = True

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return MotionSensorConfig(fields['pin_id'], fields['no_movement_timeout_s'], fields['result_name'])

    def get_datapoints(self):
        return {self.config.result_name: io.input(self.config.pin_id)}

    def is_data_ready(self, current_time):
        if self.change_detected:
            self.change_detected = False
            return True
        else:
            return False

def sensor_create(sensor_type, id, json_config):
    print("Creating sensor, for type: "+str(sensor_type))
    if sensor_type == 1:
        print("Creating GPIO")
        return MotionSensor(id, json_config)
    elif sensor_type == 2:
        print("Creating Application")
        return ApplicationSensor(id, json_config)
    elif sensor_type == 3:
        print("Creating analog sensor")
        return AnalogSensor(id, json_config)
    else:
        print("Invalid sensor type specified: " + str(sensor_type))
        return None
