# -*- coding:utf-8 -*-
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from lightning.serializers import  PointSerializer

from lightning.models import DevModel,PointModel,ServerModel
# Create your views here.

#2020.11.01
from lightning import tasks

Influxdb_TABLENAME = "test1"

class DataPostAPI(APIView):
    
    def post(self, request, format=None):
        """
        serializer = CommentSerializer(data=data)
        serializer.is_valid()
        # True
        serializer.validated_data
        """
        #res = tasks.add.delay(1,2)#注意这里一定要调用delay,不然它不是异步执行，而是同步执行
        #print(res)#异步执行的话这里返回该任务的uuid
        status = None
        try:
            print(request.data)
            ser = PointSerializer(data=request.data)
            print(request.data)

            region_id = None #类型为一个字符串
            dev_id = None #类型为一个正整数
            dev_valid = False
            dev_obj = None
            date1 = None
            server_ids = []#存放转化为int类型的服务点码（正整数类型）
            point_objs = []#存放生成的数据点对象

            server_list = [] #初始化服务码列表(字符串类型)，正整数列表
            sensor_values = []#初始化服务码对应的传感器数据，数字字符串列表

            #2020.10.08
            datasets = ServerModel.objects.all()
            datasets1 = None
            datasets2 = None

            #添加influxdb数据存储功能
            influxdb_data = []

            if ser.is_valid():#数据是否有效
                data = ser.validated_data

                for k,v in data.items():
                    if k == "address":#获得相应的地址序列
                        address = v.split("/")
                        region_id = address[0]#获得区域代码
                        dev_queryset1 = DevModel.objects.filter(region_id=region_id)

                        dev_id = int(address[1])#获得设备地址码
                        dev_queryset2 = dev_queryset1.filter(address_id=dev_id)

                        if not dev_queryset2.exists():#如果设备不存在，则不执行后续操作
                            status = "Dev not exists!"
                            print("设备不存在！")
                            break
                        dev_obj = dev_queryset2.first()#得到设备对象
                        if not dev_obj.id_valid:#如果设备未激活，则不执行后续操作
                            status = "Dev not activate!"
                            print("设备未激活！")
                            break
                        server_list = address[2:]#获得服务码列表
                        dev_valid = True #设备有效
                        #print("区域码：%s,地址码：%s,服务码：%s"%(add[0],add[1],add[2]))
                    elif k == "datetime":#获得采集日期
                        date1 = v #获得datetime格式的时间对象
                    elif k == "values":#获得传感器数据值序列
                        
                        datas = v.split("/")#获得传感器数据列表（注意传感器数据的格式为字符串）
                        if len(server_list) == len(datas):
                            sensor_values = datas
                            for j in server_list:
                                server_ids.append(int(j))

                        else:
                            status = "[1]:数据和服务码个数不对应"
                            print("数据个数：%d,服务点数：%d"%(len(server_list),len(datas)))
                            print(server_list,datas)
                    else:
                        print("无效的字段")
                #存入数据库中
                #
                #  
                datasets1 = datasets.filter(dev=dev_obj)#获得对应设备的服务码列表
                print("---------进入数据存储阶段--------")
                if datasets1.exists() and dev_valid:
                    print("---------进入数据存储阶段-[数据有效]-------")
                    count = 0
                    for i in server_ids:#需实现的部分，转换成后台定义的数据类型，并存入数据库中！
                        if datasets1.filter(serve_id=i).exists():
                            ser_obj = datasets1.filter(serve_id=i).first()#获得服务点对象
                            value = sensor_values[count]
                            #第一个路径：存入数据库
                            q1 = PointModel.objects.all()
                            if q1.filter(datetime=date1,server=ser_obj).exists():#如果同一服务点存在同时间的数据则更新该数据
                                #print("存在的哦！")
                                obj = q1.filter(datetime=date1,server=ser_obj).first()
                                if obj.value != value:
                                    obj.value = value
                                    obj.save()
                            else:
                                point = PointModel(value=value,datetime=date1,server=ser_obj)
                                point_objs.append(point)
                            #第二个路径：存入时间序列数据库
                            #存入格式说明：
                            #tag:region_id,dev_id,serve_id
                            #field:value
                            #每个数据点为一条数据
                            #采用restful的方式提交数据或直接用api进行存储
                            influxdb_point = {}
                            influxdb_point["measurement"] = Influxdb_TABLENAME
                            influxdb_point["time"] = date1.isoformat("T")
                            tags = {}
                            tags["region_id"] = region_id
                            tags["dev_id"] = dev_id
                            tags["type"] = "measurement"
                            tags["serv_id"] = i
                            influxdb_point["tags"] = tags
                            value_dict = {}
                            value_dict["value"] = value
                            influxdb_point["fields"] = value_dict
                            influxdb_data.append(influxdb_point)
                            
                        count +=1
                    #print("---------进入数据存储阶段-[开始存储数据]-------")
                    PointModel.objects.bulk_create(point_objs)
                    tasks.store_influxdb.delay(influxdb_data)#异步执行存入时间数据库
                    #print("---------进入数据存储阶段-[数据存储完毕]-------")
                else:
                    status = "Server not exists!"    
            else:
                status = ser.error_messages
        except Exception as e:
            status = "内部有错误"
            print(e)
        finally:
            
            return Response({"status":status})