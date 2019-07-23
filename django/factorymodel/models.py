from django.db import models

# Create your models here.
from django.db import models

# class Person(models.Model):
#     name = models.CharField(max_length=30)
#     age = models.IntegerField()


class worker_table(models.Model):
    workerId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30,default="暂无匹配姓名")
    timeStart = models.CharField(max_length=30)
    timeEffect = models.IntegerField()

class gatelog_table(models.Model):
    workerId = models.IntegerField()
    workerName = models.CharField(max_length=30)
    action = models.CharField(max_length=30)   # 1:in  0:out
    time = models.DateTimeField(auto_now_add =True)    # auto_now_add is create time  auto_now is update time
    #
    # def __str__(self):
    #     return ('id'+ str(self.workerId) + 'name'+ self.workerName + 'action'+  str(self.action) + 'time'+  str(self.time))



class heatmap_table(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    A = models.IntegerField(default=0)
    B = models.IntegerField(default=0)
    C = models.IntegerField(default=0)
    D = models.IntegerField(default=0)
    E = models.IntegerField(default=0)
    F = models.IntegerField(default=0)
    G = models.IntegerField(default=0)
    H = models.IntegerField(default=0)



