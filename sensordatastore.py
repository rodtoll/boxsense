__author__ = 'Rod'

import mysql.connector
import Sensors

class SensorDataStore:
    def __init__(self, db_name='test'):
        self.connection = mysql.connector.connect(user='', password='', host='127.0.0.1', database=db_name)

    def get_sensors(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * from sensors')
        sensors = [Sensors.sensor_create(sensor_type, id, config) for id, sensor_type, config in cursor]
        cursor.close()
        return sensors

