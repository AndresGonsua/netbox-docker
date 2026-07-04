from django.urls import path
from . import views

urlpatterns = [
    path('', views.RackReportView.as_view(), name='rack_report'),
    path('export/', views.RackReportExportView.as_view(), name='rack_report_export'),
]
