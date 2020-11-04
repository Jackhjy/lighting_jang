# -*- coding:utf-8 -*-
from django.db import models

from django.contrib.auth.models import User

import uuid
# Create your models here.

class DevModel(models.Model):
    uuid = models.UUIDField(verbose_name="唯一识别码",default=uuid.uuid4)
    name = models.CharField(verbose_name="设备名称",max_length=128)
    region_id = models.CharField(verbose_name="区域代码",max_length=128)
    address_id = models.PositiveSmallIntegerField(verbose_name="地址")
    create_datetime = models.DateTimeField(verbose_name="设备创建日期",auto_now_add=True)
    online_datetime = models.DateTimeField(verbose_name="设备最近一次登录时间")
    id_valid = models.BooleanField(verbose_name="该设备是否激活",default=False)
    user = models.ForeignKey(User,verbose_name="所属用户",on_delete=models.SET_NULL, blank=True, null=True)
    desc = models.TextField(verbose_name="设备描述")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name=u'保护装置'
        verbose_name_plural=u'添加保护装置'
        unique_together = ('region_id','address_id',)

CHOICES_PERMISSION = (
    ('R',"读"),
    ('W',"写"),
    ("R+W","读写")
)
class DevGroupModel(models.Model):
    uuid = models.UUIDField(verbose_name="设备组识别码",default=uuid.uuid4)
    name = models.CharField(verbose_name="组名称",max_length=128)

    devs = models.ManyToManyField(DevModel,verbose_name="设备组")
    users = models.ManyToManyField(User,verbose_name="支持的用户")
    permission = models.CharField(choices=CHOICES_PERMISSION,verbose_name="设备组操作权限",max_length=128)
    desc = models.TextField(verbose_name="设备组描述")
    class Meta:
        verbose_name=u'设备组管理'
        verbose_name_plural=u'添加设备组'    
    def __str__(self):
        return self.name
        
CHOICES_DATATYPE = (
    ("F","浮点值"),
    ("B","布尔值"),
    ("I","整数值")
)
UNIT_CHOICES = (
    ("m",u"米"),
    ("m2",u"平方米"),
    ("m3",u"立方米"),
    ("Kg",u"千克"),
    ("s",u"时间（秒）"),
    ("Ω",u"阻抗（欧姆）"),
    ("℃",u"摄氏度"),
    ("Pa",u"帕斯卡"),
    ("A",u"安培"),
    ("mA",u"毫安"),
    ("V",u"伏特"),
    ("mV",u"毫伏"),
    ("W",u"瓦特"),
    ("mW",u"毫瓦"),
    ("Var",u"无功（乏）"),
    ("VA",u"伏安"),
    ("N",u"牛顿"),
    ("Hz",u"赫兹"),
    ("m/s",u"速度（米/秒）"),
    (u"度",u"角度"),
    ("%",u"湿度（%）"),
    ("%",u"百分比(%)"),
    ("Ie",u"电流标幺值"),
    ("Bool",u'布尔值'),#用来设置前端的显示
    (" ",u"空")
)

'''
总共有几组数据：
A相泄漏电流 浮点类 mA   服务点码：1
B相泄漏电流 浮点类 mA   服务点码：2
C相泄漏电流 浮点类 mA   服务点码：3
设备温度 整数类 ℃   服务点码：4
设备电量 整数类 %   服务点码：5
A相工频电流 浮点类 A   服务点码：6
B相工频电流 浮点类 A   服务点码：7
C相工频电流 浮点类 A   服务点码：8
A是否遭雷击 布尔类 无   服务点码：9
B是否遭雷击 布尔类 无   服务点码：10
C是否遭雷击 布尔类 无   服务点码：11
N是否遭雷击 布尔类 无  服务点码：12
'''
class ServerModel(models.Model):
    serve_id = models.PositiveSmallIntegerField(verbose_name="服务点码")
    name = models.CharField(verbose_name="服务名称",max_length=128)
    value_type = models.CharField(verbose_name="数据类型",max_length=128,choices=CHOICES_DATATYPE)
    value_sign = models.CharField(verbose_name="符号",choices=UNIT_CHOICES,max_length=128)
    dev = models.ForeignKey(DevModel,verbose_name="所属设备",on_delete=models.CASCADE)
    desc = models.TextField(verbose_name="服务描述")
    class Meta:
        verbose_name=u'设备服务管理'
        verbose_name_plural=u'添加设备服务'
    def __str__(self):
        return self.name
#可以考虑region_id/address_id/serve_id的post形式来存储数据
class PointModel(models.Model):
    value = models.CharField(verbose_name="数据值",max_length=128)
    datetime = models.DateTimeField(verbose_name="采集时间")
    server = models.ForeignKey(ServerModel,verbose_name="所属服务",on_delete=models.CASCADE)
    class Meta:
        verbose_name=u'设备服务采集点'
        verbose_name_plural=u'添加设备服务采集点'
    def __str__(self):
        return self.value