from django.urls import path
from .views import mark_entry_view
from .views import report_card_view
from .views import export_results_view

urlpatterns = [
path('mark-entry/<int:exam_id>/', mark_entry_view, name='mark_entry'),
path('report-card/', report_card_view, name='report_card'),
path('export-results/', export_results_view, name='export_results'),
]