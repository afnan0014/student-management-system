from django.urls import path
from . import views
from .views import course_subjects, view_subjects_by_course

urlpatterns = [
    # List views
    path('departments/', views.department_list, name='department_list'),
    path('courses/', views.course_list, name='course_list'),
    
    
    # Add views
    path('departments/add/', views.add_department, name='add_department'),
    path('courses/add/', views.add_course, name='add_course'),
    
    # Course subjects view
    path('courses/<int:course_id>/subjects/', course_subjects, name='course_subjects'),
    path('course/<int:course_id>/subjects/', views.view_subjects_by_course, name='view_subjects_by_course'),


    # Edit views
    path('departments/edit/<int:department_id>/', views.edit_department, name='edit_department'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    
    
    # Delete views
    path('departments/delete/', views.delete_departments, name='delete_departments'),
    path('courses/delete/', views.delete_courses, name='delete_courses'),
    
]