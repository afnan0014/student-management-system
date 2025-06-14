from django.urls import path
from . import views
from .views import create_assignment

urlpatterns = [
    path('', views.assignment_list, name='assignment_list'),
    path('create/', views.create_assignment, name='create_assignment'),
    path('edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('view/<int:assignment_id>/', views.view_assignment, name='view_assignment'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('submissions/<int:assignment_id>/', views.view_submissions, name='view_submissions'),
    path('get-students/', views.get_students_by_course, name='get_students_by_course'),
    path('get-subjects/', views.get_subjects_by_course, name='get_subjects_by_course'),  # New endpoint
    path('create/', create_assignment, name='create_assignment'),
]