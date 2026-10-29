from django.urls import path
from .views import (
    DeliverableListCreateView, DeliverableDetailView,
    DeliverableVersionCreateView
)

urlpatterns = [
    path('', DeliverableListCreateView.as_view(), name='deliverable-list-create'),
    path('<int:pk>/', DeliverableDetailView.as_view(), name='deliverable-detail'),
    path('versions/', DeliverableVersionCreateView.as_view(), name='deliverable-version-create'),
]

