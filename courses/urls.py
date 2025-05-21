from django.urls import path
from . import views

urlpatterns = [
    # List views
    path('departments/', views.department_list, name='department_list'),
    path('courses/', views.course_list, name='course_list'),
    path('subjects/', views.subject_list, name='subject_list'),
    
    # Add views
    path('departments/add/', views.add_department, name='add_department'),
    path('courses/add/', views.add_course, name='add_course'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    
    # Edit views
    path('departments/edit/<int:department_id>/', views.edit_department, name='edit_department'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('subjects/edit/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    
    # Delete views
    path('departments/delete/', views.delete_departments, name='delete_departments'),
    path('courses/delete/', views.delete_courses, name='delete_courses'),
    path('subjects/delete/', views.delete_subjects, name='delete_subjects'),
]