from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    path('export/students/csv/', views.export_students_csv, name='export_students_csv'),
    path('export/students/pdf/', views.export_students_pdf, name='export_students_pdf'),
]
