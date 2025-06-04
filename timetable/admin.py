from django.contrib import admin
from .models import TimetableEntry, Holiday

admin.site.register(TimetableEntry)
admin.site.register(Holiday)
