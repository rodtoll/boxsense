__author__ = 'Rod'

import httplib
import json
import datetime


class DataFeed:
    def __init__(self, json_config):
        self.config = self.json_to_config(json_config)

    def upload_datapoints(self, data_points):
        None

    def json_to_config(self, json_config):
        None

class CosmDataFeed(DataFeed):
    def __init__(self, json_config):
        DataFeed.__init__(self, json_config)

    def build_cosm_uri(self, data_key):
        if self.config.feeds.has_key(data_key):
            cosm_uri = 'http://api.cosm.com/v2/feeds/' + str(self.config.feed_id) + '/datastreams/' + \
                       str(self.config.feeds[data_key]) + "/datapoints"
            print("Cosm URI: " + cosm_uri)
            return cosm_uri
        else:
            print("No mapping found for data item: " + data_key)
            return None

    def json_to_config(self, json_config):
        decoder = json.JSONDecoder()
        fields = decoder.decode(json_config)
        return CosmConfig(fields['host'], fields['port'], fields['api_key'], fields['feed_id'], fields['feeds'])

    def upload_datapoints(self, data_points):
        current_time = datetime.datetime.utcnow()
        headers = {"X-ApiKey" : self.config.api_key}
        for data_key, data_value in data_points.items():
            if data_value is not None:
                request_uri = self.build_cosm_uri(data_key)
                if request_uri is not None:
                    connection = httplib.HTTPConnection(self.config.host, self.config.port)
                    request_body = '{ "datapoints":[{"at":"' + current_time.strftime("%Y-%m-%dT%H:%M:%SZ") + '","value":"' + str(data_value) + '"}]}'
                    print("Making request to: " + request_uri)
                    print("Request is:")
                    print(request_body)
                    print("-----")
                    connection.request("POST", request_uri, request_body, headers)
                    response = connection.getresponse()
                    print("Status is: " + str(response.status))
                    print("Reason is: " + str(response.reason))

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

def datafeed_create_feed(feed_type, json_config):
    if feed_type == 1:
        return None
    elif feed_type == 2:
        return CosmDataFeed(json_config)
    else:
        print("Invalid feed type specified: " + str(feed_type))
        return None

