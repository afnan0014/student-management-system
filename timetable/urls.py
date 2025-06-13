from django.urls import path
from .views import (
    timetable_list_view, add_timetable_entry, edit_timetable_entry,
    delete_timetable_entries,student_timetable_view,staff_timetable_view
)

urlpatterns = [
    path('admin/', timetable_list_view, name='timetable_list'),
    path('admin/add/', add_timetable_entry, name='add_timetable_entry'),
    path('admin/edit/<int:pk>/', edit_timetable_entry, name='edit_timetable_entry'),
    path('admin/delete/', delete_timetable_entries, name='delete_timetable_entries'),
    path('student/', student_timetable_view, name='student_timetable'),
    path('staff/', staff_timetable_view, name='staff_timetable'),
]