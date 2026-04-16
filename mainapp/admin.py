from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Party)
admin.site.register(Transaction)
admin.site.register(Purchase)
admin.site.register(Processing)
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(Salary)