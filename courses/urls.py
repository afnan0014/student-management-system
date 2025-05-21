from django.urls import path
from . import views

urlpatterns = [
    path('add-department/', views.add_department, name='add_department'),
    path('departments/', views.department_list, name='department_list'),

    path('add-course/', views.add_course, name='add_course'),
    path('courses/', views.course_list, name='course_list'),

    path('add-subject/', views.add_subject, name='add_subject'),
    path('subjects/', views.subject_list, name='subject_list'),



]
