from django.urls import path
from .views import DashboardReportsView

urlpatterns = [
    path('dashboard/', DashboardReportsView.as_view(), name='dashboard-reports'),
]

