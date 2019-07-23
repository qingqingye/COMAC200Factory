from django.contrib import admin


# Register your models here.

from factorymodel.models import *
admin.site.register(heatmap_table)
admin.site.register(gatelog_table)