from django.urls import path
from . import views

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('student_view/', views.student_attendance_view, name='student_view'),
    path('export/', views.export_attendance_csv, name='export_attendance_csv'),
    path('attendance_report/', views.admin_view_attendance, name='admin_view_attendance'),  # ✅ updated name
]
