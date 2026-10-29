from django.urls import path
from .views import (
    InvoiceListCreateView, InvoiceDetailView,
    PaymentRecordCreateView, InvoicePDFDownloadView
)

urlpatterns = [
    path('', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('<int:invoice_pk>/payments/', PaymentRecordCreateView.as_view(), name='invoice-record-payment'),
    path('<int:invoice_pk>/pdf/', InvoicePDFDownloadView.as_view(), name='invoice-pdf-download'),
]

