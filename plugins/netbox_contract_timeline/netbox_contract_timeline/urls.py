from django.urls import path
from . import views

urlpatterns = [
    path('', views.ContractTimelineView.as_view(), name='timeline'),
]
