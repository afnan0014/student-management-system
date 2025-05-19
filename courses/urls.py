from django.urls import path
from . import views

urlpatterns = [
    path('add/department/', views.add_department, name='add_department'),
    path('add/course/', views.add_course, name='add_course'),
    path('add/subject/', views.add_subject, name='add_subject'),
]
