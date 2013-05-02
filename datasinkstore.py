__author__ = 'Rod'

import mysql.connector
import DataSink

class DataSinkStore:
    def __init__(self, db_name='test'):
        self.connection = mysql.connector.connect(user='', password='', host='127.0.0.1', database=db_name)

    def get_sinks(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * from feeds')
        feeds = [DataSink.datasink_create(feed_type, config) for id, feed_type, config in cursor]
        cursor.close()
        return feeds
