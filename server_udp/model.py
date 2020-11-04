# -*- coding:utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import os
import datetime
import requests
import json

#学习资源网址：https://www.cnblogs.com/lsdb/p/9835894.html

#创建引擎
#BASE_DIR = os.path.dirname(__file__)
#DB_FILEPAH = '\\'.join([BASE_DIR,"buf.db"])
#第一步：建立引擎
engine = sqlalchemy.create_engine("sqlite:///test.db",echo=False)
#第二步：定义映射
Base = declarative_base()
class PostData(Base):
    __tablename__ = "test1"
    #必须指定一个初键
    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
    client_addr = sqlalchemy.Column(sqlalchemy.String(128),nullable=False)
    data = sqlalchemy.Column(sqlalchemy.String(512),nullable=False)
    datetimenow = sqlalchemy.Column(sqlalchemy.DateTime)

class Handler(object):
    def __init__(self):
        #Base.metadata.create_all(engine)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        self.session = Session()
        self.poplen = 0 #一次返回的数据对象的数量，0：表示无限制
        self.header = {'Content-Type':'application/json','Host': "127.0.0.1"}
        self.url = "http://localhost:8000/lightning/api/"
    
    def pushdata(self,data,addr):
        #生成数据对象
        postdata = PostData(client_addr=addr,data=data,datetimenow=datetime.datetime.now())
        self.session.add(postdata)
        self.session.commit()

    def popdata(self,length=0):
        if length == 0:
            objs =self.session.query(PostData).all()
        else:
            objs = self.session.query(PostData).limit(length).all()#返回限定数量的数据对象
        return objs

    def deletedata(self,obj):
        self.session.delete(obj)
        self.session.commit()

    def postdata(self,data_dict,client_addrlist):
        firts_commitok = False
        try:
            response = requests.post(self.url,headers=self.header,data=json.dumps(data_dict))
            if response.status_code == 200:
                firts_commitok = True
                objs = self.popdata()
                if objs:
                    for obj in objs:
                        response = requests.post(self.url,headers=self.header,data=obj.data)
                        if response.status_code == 200:
                            self.session.delete(obj)
                        else:#如果连接数据主站失败
                            break
                    self.session.commit()
                else:#数据库无可用的上传对象
                    pass
                print("上传成功！")
            else:
                self.pushdata(json.dumps(data_dict),":".join([str(client_addrlist[0]),str(client_addrlist[1])]))
                print("上传失败！")
                print(response.status_code)
        except Exception as e:
            if not firts_commitok:
                self.pushdata(json.dumps(data_dict),":".join([str(client_addrlist[0]),str(client_addrlist[1])]))
            print("数据主站不能访问")

if __name__ == "__main__":

    #第三步：创建数据表，如果已存在，则跳过这一步
    Base.metadata.create_all(engine)

    #第四步：建立会话
    #只有建立了会话才能增删查改数据库中的数据
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    #创建Session类实例
    session = Session()

    #第五步：向数据库中插入数据
    #postdata = PostData(client_addr="192.168.1.1:8848",data='{"addr":"789"}',datetimenow=datetime.datetime.now())
    #插入一条数据
    #session.add(postdata)
    #插入多条数据
    #session.add_all([obj1,obj2,...])
    #提交数据
    #session.commit()

    check_objs=session.query(PostData).all()
    #check_obj=session.query(PostData).first()
    #print(check_obj)
    #print(check_objs)
    #删除对象列表
    print("数据条数：%d"%len(check_objs))

    #for i in check_objs:
        #session.delete(i)
    #session.commit()
    #check_objs=session.query(PostData).all()
    #print(check_objs)

