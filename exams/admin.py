from django.contrib import admin

# Register your models here.
from .models import Exam, Mark, Result

admin.site.register(Exam)
admin.site.register(Mark)
admin.site.register(Result)

