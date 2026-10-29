from django.urls import path
from .views import RevisionListCreateView, RevisionDetailView

urlpatterns = [
    path('', RevisionListCreateView.as_view(), name='revision-list-create'),
    path('<int:pk>/', RevisionDetailView.as_view(), name='revision-detail'),
]

