from django.urls import path
from .views import add_timetable_entry, staff_timetable_view, student_timetable_view

urlpatterns = [
    path('admin/add/', add_timetable_entry, name='add_timetable_entry'),
    path('staff/', staff_timetable_view, name='staff_timetable'),
    path('student/', student_timetable_view, name='student_timetable'),
]
