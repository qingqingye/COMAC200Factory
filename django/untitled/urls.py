"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


#make connect between URL and what to return
from django.contrib import admin
from django.urls import path
from factorymodel import views

from apscheduler.scheduler import Scheduler


dataCenter = views.DataProcessor()
sched = Scheduler()  # 实例化，固定格式

@sched.interval_schedule(seconds=100)  # 装饰器，seconds=60意思为该函数为1分钟运行一次
def mytask():
    views.TableHeatmap()
sched.start()  # 启动该脚本

urlpatterns = [
    # path('', fac_views.index),  # new
    # path('add/', fac_views.add, name='add'),
    # path('add/<int:a>/<int:b>/', fac_views.add2, name='add2'),
    # path('dict/',fac_views.dict,name='dict'),
    path('factory/count', dataCenter.getWorkerCount,name='count'),
    path('factory/statistic', dataCenter.getWorkerStatistic, name='statistic'),
    path('gate', dataCenter.getGateInfoAsync, name='gate'),
    path('heatmap', dataCenter.getHeatmap, name='heatmap'),

    path('dashboard/avgRate',dataCenter.avg,name='avg'),
    path('dashboard/gatehis', dataCenter.hositoryReturn , name='gatehis'),
    path('heatmapTable',dataCenter.tableHeatmap,name= 'heatmapTable'),
    path('dashboard/table',dataCenter.workrate,name='workrate'),
    path('dashboard/counter',dataCenter.weekPeople,name='workweek'),
    path('admin/', admin.site.urls),
]

