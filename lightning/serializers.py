# -*- coding:utf-8 -*-
from rest_framework import serializers
from lightning.models import PointModel,DevModel,DevGroupModel,ServerModel

class PointSerializer(serializers.Serializer):

    address = serializers.CharField(max_length=256,min_length=5)#"region_id/address_id/server_id1/server_id2/server_id3....."
    values = serializers.CharField(max_length=256,min_length=1)#"sensor1,sensor2,sensor3,........""
    datetime = serializers.DateTimeField()# (eg '2013-01-29T12:34:56.000000Z')