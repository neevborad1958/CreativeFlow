from django.urls import path
from .views import ApprovalListCreateView, ApprovalDetailView

urlpatterns = [
    path('', ApprovalListCreateView.as_view(), name='approval-list-create'),
    path('<int:pk>/', ApprovalDetailView.as_view(), name='approval-detail'),
]

