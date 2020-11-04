from django.contrib import admin

# Register your models here.

from lightning.models import DevModel,DevGroupModel,ServerModel,PointModel

class DevModelAdmin(admin.ModelAdmin):
    search_fields = ("name",)

class DevGroupModelAdmin(admin.ModelAdmin):
    search_fields = ("name",)

class ServerModelAdmin(admin.ModelAdmin):
    search_fields = ("name",)

class PointModelAdmin(admin.ModelAdmin):
    search_fields = ("datetime",)
    list_display = ("server","value","datetime")
admin.site.site_header=u'雷击监测系统'
admin.site.site_title=u'监测系统'

admin.site.register(DevModel,DevModelAdmin)
admin.site.register(DevGroupModel,DevGroupModelAdmin)
admin.site.register(ServerModel,ServerModelAdmin)
admin.site.register(PointModel,PointModelAdmin)