__author__ = 'Rod'

import httplib
import json
import datetime
import ISY
import mysql.connector

class DataSink:
    def __init__(self, json_config):
        self.config = self.json_to_config(json_config)

    def upload_datapoints(self, current_time, sensor, data_points):
        None

    def json_to_config(self, json_config):
        None

    def datetime_to_utc_str(self, date):
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")


class CosmDataSink(DataSink):
    def __init__(self, json_config):
        DataSink.__init__(self, json_config)

    def build_cosm_uri(self, data_key):
        if self.config.feeds.has_key(data_key):
            cosm_uri = 'http://api.cosm.com/v2/feeds/' + str(self.config.feed_id) + '/datastreams/' + \
                       str(self.config.feeds[data_key]) + "/datapoints"
            return cosm_uri
        else:
            return None

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return CosmConfig(fields['host'], fields['port'], fields['api_key'], fields['feed_id'], fields['feeds'])

    def upload_datapoints(self, current_time, sensor, data_points):
        headers = {"X-ApiKey" : self.config.api_key}
        for data_key, data_value in data_points.items():
            if data_value is not None:
                request_uri = self.build_cosm_uri(data_key)
                if request_uri is not None:
                    connection = httplib.HTTPConnection(self.config.host, self.config.port)
                    request_body = '{ "datapoints":[{"at":"' + self.datetime_to_utc_str(current_time) + '","value":"' + str(data_value) + '"}]}'
                    connection.request("POST", request_uri, request_body, headers)
                    response = connection.getresponse()
                    if response.status != 200:
                        print("Status is: " + str(response.status) + " Reason: " + str(response.reason))

class CosmConfig:
    def __init__(self, host, port, api_key, feed_id, feeds):
        self.host = host
        self.port = port
        self.api_key = api_key
        self.feed_id = feed_id
        self.feeds = feeds

    def get_json(self):
        encoder = json.JSONEncoder()
        return encoder.encode(self.__dict__)

class ISYDataSink(DataSink):
    def __init__(self, json_config):
        DataSink.__init__(self, json_config)
        self.isy = ISY.Isy(addr=self.config.address, userl=self.config.username, userp=self.config.password)

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return ISYConfig(fields['address'], fields['username'], fields['password'], fields['variables'])

    def upload_datapoints(self, current_time, sensor, data_points):
        for key, value in data_points.items():
            if value is not None:
                if self.config.variables.has_key(key):
                    isy_variable_name = self.config.variables[key]
                    self.isy.var_set_value(isy_variable_name, value)

class ISYConfig:
    def __init__(self, address, username, password, variables):
        self.address = address
        self.username = username
        self.password = password
        self.variables = variables

    def get_json(self):
        encoder = json.JSONEncoder()
        return encoder.encode(self.__dict__)

class MySqlDataSink(DataSink):
    def __init__(self, json_config):
        DataSink.__init__(self, json_config)
        self.connection = mysql.connector.connect(user='root', password='Alpha1Romero', host='127.0.0.1', database='sensor')

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return MySqlDataSinkConfig(fields['database_name'], fields['table_name'], fields['field_map'])

    def upload_datapoints(self, current_time, sensor, data_points):
        for key, value in data_points.items():
            if value is not None:
                if self.config.field_map.has_key(key):
                    cursor = self.connection.cursor()
                    cursor.execute("INSERT INTO "+self.config.table_name+"(sensor_id, field_id, timestamp, reading) VALUES (%s, %s, %s, %s)",
                        (sensor.id, self.config.field_map[key], self.datetime_to_utc_str(current_time), value))
                    cursor.close()

class MySqlDataSinkConfig:
    def __init__(self, database_name, table_name, field_map):
        self.database_name = database_name
        self.table_name = table_name
        self.field_map = field_map

    def get_json(self):
        encoder = json.JSONEncoder()
        return encoder.encode(self.__dict__)

def datasink_create(feed_type, json_config):
    if feed_type == 1:
        return MySqlDataSink(json_config)
    elif feed_type == 2:
        return CosmDataSink(json_config)
    elif feed_type == 3:
        return ISYDataSink(json_config)
    else:
        print("Invalid feed type specified: " + str(feed_type))
        return None

