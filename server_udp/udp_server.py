# -*- coding:utf-8 -*-
import socketserver
import threading
import socket
import time
import datetime
import struct
import json
import requests

#以下是相关的日志模块的定义
import logging as lg
lg.basicConfig(level=lg.DEBUG)
logger = lg.getLogger(__name__)
handler = lg.FileHandler("log_udp.txt")
handler.setLevel(lg.INFO)
formatter = lg.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

from model import Handler
from parse import crc16


import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


#第一步：建立引擎
engine = sqlalchemy.create_engine("sqlite:///test.db",echo=True)
#第二步：定义映射
Base = declarative_base()

DEBUG= True
class ClientClass(object):
    fmt201 = "!4B3H2B2x"#从机主动上送的泄露电流代码
    fmt202 = "!10Bxc3H2x"#从机主动上送的雷击信息代码
    fmt101 = "!13B"#主机发给从机的校时信息格式
    def __init__(self,handler_obj):
        self.handler = handler_obj
        self.socket = handler_obj.request[1]
        self.socket.settimeout(10)#必须要设置

        self.region_name = "jangjunshan"
        self.dev_id = None
        self.is_first = True#是否为第一次握手主机
        self.future_data = []#需要发送给从机的数据列表
        self.handle_data = Handler()#生成一个处理对象
    def handle_req(self):
        count1 = 0
        while True:
            try:
                data = None
                data_str = None
                if self.is_first:#第一次访问
                    data = self.handler.request[0]
                    data_str = data.hex()
                    self.is_first = False#
                    count1 = count1+1
                    if DEBUG:
                        print("第%d次收到数据"%(count1))
                        print("{}:{}client send data for me:{}".format(self.handler.client_address[0],self.handler.client_address[1],data.hex()))
                    logger.debug("{}:{}client send data for me:{}".format(self.handler.client_address[0],self.handler.client_address[1],data.hex()))
                else:#第二次及后续访问
                    if self.future_data:#如果有下次要发送的数据
                        data_buf = self.future_data.pop()
                        self.socket.sendto(data_buf,self.handler.client_address)#从这里发送数据到子站
                        logger.debug("send data to {}:{}client:{}".format(data_buf.hex(),self.handler.client_address[0],self.handler.client_address[1]))
                    data,addr = self.socket.recvfrom(1024)
                    data_str = data.hex()
                    count1 = count1+1
                    if DEBUG:
                        print("第%d次收到数据"%(count1))
                        print("{}:{}client send data for me:{}".format(self.handler.client_address[0],self.handler.client_address[1],data.hex()))
                    logger.debug("{}:{}client send data for me:{}".format(self.handler.client_address[0],self.handler.client_address[1],data.hex()))
                #crc16校验
                if not crc16(data[:-2],True,True) == data.hex()[-4:].upper():
                    #校验未通过的异常处理
                    if DEBUG:
                        print("计算得到的值为：%s,从机上送的校验值为：%s"%(crc16(data[0:-4],True,True),data_str[-4:].upper()))
                    break
                
                #数据处理
                if data_str[2:4] == "20":#功能码20H
                    if data_str[4:6] == "10":#地址为10H（为从机主动上送的三相泄露电流信息）
                        data_temp = struct.unpack(ClientClass.fmt201,data)#得到的是1,2,3,4,5的服务点码
                        self.dev_id = data_temp[0]
                        address_list = [self.region_name,str(self.dev_id),"1","2","3","4","5"]
                        datas_temp =  [float(data_temp[4])/100.00,float(data_temp[5])/100.00,float(data_temp[6])/100.00,float(data_temp[7]),float(data_temp[8])]
                        datas_list = ["{:.2f}".format(i) for i in datas_temp]
                        
                        #上传到数据管理后台
                        
                        data_dict = {"address":'/'.join(address_list),"values":'/'.join(datas_list),"datetime":datetime.datetime.now().isoformat()}#时间为当前服务器的时间
                        #开始处理数据
                        self.handle_data.postdata(data_dict,self.handler.client_address)
                        logger.debug("Post data to host:%s"%data_dict)
                        
                        self.future_data.append(self.handler.request[0])##将本次从机发送给主机的命令原样添加到数据发送队列中去。2020.10.27
                        if DEBUG:
                            print(" send data to {}:{}client:{}".format(data.hex(),self.handler.client_address[0],self.handler.client_address[1]))
                        #time.sleep(0.5)#去除延时部分，可能导致连接失效！2020.10.27
                        #将时间校对时间的命令添加到数据发送队列中去。2020.10.27
                        now_temp = datetime.datetime.now()
                        if now_temp.day in [1,14,21,27]:#每个月的1号、14号、21号及27号下发时间校准命令
                            #准备校对时间的命令数据
                            now = now_temp
                            m_s_time = [0x01,0x10,0x00,0x20,0x00,0x03,0x06,now.year,now.month,now.day,now.hour,now.minute,now.second]
                            bytes_time = struct.pack(ClientClass.fmt101,0x01,0x10,0x00,0x20,0x00,0x03,0x06,now.year-2000,now.month,now.day,now.hour,now.minute,now.second)
                            crc_value = crc16(m_s_time,True,True).lower()
                            bytes_crc1 = bytes([eval("0x"+crc_value[0:2]),eval("0x"+crc_value[-2:])])
                            time_byte = bytes_time + bytes_crc1#得到时间校验命令字符串
                            #上述数据准备完毕
                            self.future_data.append(time_byte)
                            logger.debug("校准时间命令已生成")
                            if DEBUG:
                                print("send data to {}:{}client:{}".format(time_byte.hex(),self.handler.client_address[0],self.handler.client_address[1]))
                    elif data_str[4:6] == "15":#地址为15H（从机主动上送的雷击时间和工频电流）
                        data_temp = struct.unpack(ClientClass.fmt202,data)#得到的是6,7,8,9,10,11的服务点码
                        self.dev_id = data_temp[0]
                        address_list = [self.region_name,str(self.dev_id),"6","7","8","9","10","11","12"]
                        #------三相电流的提取----------
                        datas_temp2 =  [float(data_temp[11])/100.00,float(data_temp[12])/100.00,float(data_temp[13])/100.00]
                        datas_list2 = ["{:.2f}".format(i) for i in datas_temp2]
                        #-----------------------------
                        #------雷击时间的提取----------
                        year = 2000+data_temp[4]
                        month = data_temp[5]
                        day = data_temp[6]
                        hour = data_temp[7]
                        minute = data_temp[8]
                        second = data_temp[9]
                        #-----------------------------
                        #-------雷击位置的提取---------0000NABC
                        bits_byte = data_temp[10]
                        bits_str = "{:08b}".format(eval("0x"+bits_byte.hex()))
                        datas_list1 = [bits_str[5],bits_str[6],bits_str[7],bits_str[4]]
                        datas_list = datas_list2+datas_list1
                        #--------------------------------------
                        
                        data_dict = {"address":'/'.join(address_list),"values":'/'.join(datas_list),"datetime":datetime.datetime(year,month,day,hour,minute,second).isoformat()}
                        self.handle_data.postdata(data_dict,self.handler.client_address)
                        logger.debug("Post data to host:%s"%data_dict)
                        if DEBUG:
                            print(" send data to {}:{}client:{}".format(data.hex(),self.handler.client_address[0],self.handler.client_address[1]))
                                               
                        self.future_data.append(self.handler.request[0])#将本次从机发送给主机的命令原样添加到数据发送队列中去。2020.10.27
                    else:
                        #地址码不匹配的处理流程
                        pass
                    if DEBUG:
                        print("得到解析后的数据为：",data_temp)
                    
                elif data_str[2:4] == "10":#功能码10H:从机返回日期的设定情况
                    if DEBUG:
                        print("从机已经收到校时命令！")
                    logger.debug("从机已收到时间校准命令！")
                elif data_str[2:4] == "03":#功能码03H
                    pass
                else:
                    #无匹配的功能码处理流程
                    pass


                #数据返回
            except Exception as e:
                #异常处理
                print(e)
                break



class ThreadUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client = ClientClass(self)
        if DEBUG:
            print(datetime.datetime.now(),self.client_address[0],self.client_address[1])
        client.handle_req()
        #time.sleep(50)
    
    def setup(self):
        print("开始的线程总数为：%d"%(len(threading.enumerate())))
        print("处理已经开始")

    def finish(self):
        print("结束时的线程总数为：%d"%(len(threading.enumerate())-1))
        print("处理已经结束")

class UDPServer(socketserver.ThreadingUDPServer):
    def handle_timeout(self):
        print("已经超时了！")
if __name__ == "__main__":
    HOST,PORT = "localhost",8849
    server = UDPServer((HOST,PORT),ThreadUDPRequestHandler)
    server.timeout = 20.0#设置超时时间为20秒
    with server:
        ip,port = server.server_address

        server_thread = threading.Thread(target=server.serve_forever)

        server_thread.daemon = True #将该线程设置为守护线程
        server_thread.start()
        print("Server loop running in thread:",server_thread.name)

        server_thread.join() #要等待该线程结束主线程才退出

