#-*- coding:utf-8 -*-
from __future__ import absolute_import,unicode_literals
from celery import shared_task
from jangjunshan.celery import app
import time
from influxdb import InfluxDBClient
INFLUXDB_HOST = "116.62.199.222"
INFLUXDB_PORT = 8086
NAME = "jangjunshan"
PASSWORD = "123"
DATABASE_NAME = "test1"
@shared_task
def add(x,y):
    time.sleep(10)
    return x+y

'''
#在django里面不使用这种方法
@app.task
def add(x,y):
    time.sleep(10)
    return x+y
'''
@shared_task
def store_influxdb(points):
    if not isinstance(points,list):
        raise ValueError("Need a list")
    client = InfluxDBClient(INFLUXDB_HOST,INFLUXDB_PORT,NAME,PASSWORD,DATABASE_NAME)
    #db_list = client.get_list_database()#这些操作需要管理员权限的
    #if  DATABASE_NAME not in db_list:
        #client.create_database(DATABASE_NAME)
    client.write_points(points)
    return "ok!"