## 操作记录
### 生成超级用户
- ID:jack
- MM:123

### 基本配置及添加suit
- 基本配置如下：
```python

#配置支持中文
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Chongqing'
```
- suit配置如下：
```python

# pip install django-suit

INSTALLED_APPS = [
    'suit',
    'django.contrib.admin',
    #...
    #...
]

SUIT_CONFIG = {
    'ADMIN_NAME': '苹果树',
    'MENU': ({'label': '用户',
              'app': '用户',
              'models': ('UserProfile',)},
             ),
    # 每一个字典表示左侧菜单的一栏
    # label表示name，app表示上边的install的app，models表示用了哪些models
}
```
### 安装的其他模块
#### SQLAlchemy
- date:2020.10.27
- pip install SQLAlchemy


#### pip3的安装
- sudo apt-get install python3-pip

#### sqlite3语法
- .tables:展示所有的表
- select * from test1:获得表中的所有对象
- delete from test1:删除test1表中的所有记录
- delete from test1 where id=10:删除id=10的数据

### 从机上传的数据解析
#### 原始数据
```python
import struct
bytes1 = 0x0120100800c60046008e0e641e37 #从机主动上传的泄露电流的数据
fmt1  = struct.unpack()
```




### 程序调整
#### 主站连接从机不稳定，连续交互两到三轮数据后就出现重新连接的情况？
```python
# 故障重现

```

### 程序开发及相关软件安装历史记录
#### 2020.11.01
- pip install celery
- pip isntall redis
- celery.exe -A jangjunshan worker:在C:\Users\Administrator\Documents\Python\Project\jangjunshan文件夹下启动celery
- 在windows下安装了redis服务
- redis-server.exe redis.windows.conf:启动redis服务，要注意在配置文件中须指定绑定的IP，我这里指定了127.0.0.1

> （1）一般情况使用的是从celeryapp中引入的app作为的装饰器：@app.task
> （2）django那种在app中定义的task则需要使用@shared_task

```cmd
#根据返回的任务uuid（a745af24-f466-448e-a016-8397a64f2557），获得需要的执行结果：
C:\Users\Administrator\Documents\Python\Project\jangjunshan>redis-cli.exe
127.0.0.1:6379> GET celery-task-meta-a745af24-f466-448e-a016-8397a64f2557
"{\"status\": \"SUCCESS\", \"result\": 3, \"traceback\": null, \"children\": [], \"date_done\": \"2020-11-01T05:30:07.820242\", \"task_id\": \"a745af24-f466-448e-a016-8397a64f2557\"}"
```

- pip install django-celery-results#用来存储相应的执行结果
```python
#settings.py
INSTALLED_APPS = (
    ...,
    'django_celery_results',
)
#CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0' # BACKEND配置，这里使用redis
CELERY_RESULT_BACKEND = 'django-db'  #使用django orm 作为结果存储
```
- python .\manage.py migrate django_celery_results#生成相应的数据表

- 错误：
```
ValueError: not enough values to unpack (expected 3, got 0)

#解决方法
#运行：celery worker -A projname --pool=solo -l info
#这里在命令里面添加了--pool=solo就可以解决问题啦！
```

- pip install influxdb;
- 设计influxdb的数据采集表结构
```python
data = {
    "measurement":"test1,
    "time":datetime,
    "tags":{
        "region_id":"jangjunshan",
        "dev_id":2,
        "type":"measurement",#measurement:表示采集事件
        "serve_id":1
    },
    "fields":{
        "value":1.00
    }
}
```
- influxd常用命令：https://blog.csdn.net/xtj332/article/details/80525855

- echo_supervisord_conf:在数据库主机上生成supervisord配置文件


### 部署
#### 配置相应的数据后端
- 在settings.py文件中设置默认的数据库后端是用哪一种
- 在settings.py文件中配置celery异步存储队列使用的redis后端访问接口
- 在server_udp/model.py中配置需要的数据主站api的URL
- 在server_udp/udp_server.py中配置udp服务监听的端口和资源

#### 服务启动顺序
- 先启动udp_server.py,构建和从机的通讯；
- 启动celery,准备好异步处理流程；
- 最后启动django服务后端，可考虑使用nginx做后端的负载均衡；