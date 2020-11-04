#-*- coding:utf-8 -*-
import influxdb

INFLUXDB_HOST = "116.62.199.222"
INFLUXDB_PORT = 8086
NAME = "jangjunshan"
PASSWORD = "123"
DATABASE_NAME = "tests"
client = influxdb.InfluxDBClient(INFLUXDB_HOST,INFLUXDB_PORT,NAME,PASSWORD,DATABASE_NAME)
databases = client.get_list_database()
#print(databases)