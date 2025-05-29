from django.urls import path
from .views import report_card_view,staff_mark_entry_spreadsheet
from .views import export_results_view, create_exam, exam_list, delete_exams

urlpatterns = [
path('staff/mark-entry/', staff_mark_entry_spreadsheet, name='staff_mark_entry_spreadsheet'),
path('report-card/', report_card_view, name='report_card'),
path('export-results/', export_results_view, name='export_results'),
path('exams/create/', create_exam, name='create_exam'),
path('', exam_list, name='exam_list'),
path('delete/',delete_exams, name='delete_exams'),

]