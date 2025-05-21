from django.urls import path
from . import views

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark_attendance'),  # Staff marks attendance
    path('view/', views.student_attendance_view, name='student_attendance'),  # Student views attendance
]
