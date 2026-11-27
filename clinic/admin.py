from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Doctor)
admin.site.register(Specialization)
admin.site.register(Appointment)
admin.site.register(Review)
admin.site.register(EmailConfirm)