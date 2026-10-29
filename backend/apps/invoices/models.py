from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.clients.models import Client
from apps.projects.models import Project

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issued_invoices')
    issue_date = models.DateField()
    due_date = models.DateField()
    currency = models.CharField(max_length=10, default='USD')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True, default='Thank you for your business. Payment is due within 14 days.')
    terms = models.TextField(blank=True, default='Late payments may be subject to a 5% monthly fee.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']

    @property
    def balance_due(self):
        return max(Decimal('0.00'), self.total - self.amount_paid)

    def calculate_totals(self):
        calculated_subtotal = sum(item.line_total for item in self.items.all())
        self.subtotal = calculated_subtotal
        tax_amount = (self.subtotal * (self.tax_rate_percent / Decimal('100.0'))).quantize(Decimal('0.01'))
        calculated_total = (self.subtotal + tax_amount - self.discount_amount).quantize(Decimal('0.01'))
        self.total = max(Decimal('0.00'), calculated_total)

        if self.amount_paid >= self.total and self.total > Decimal('0.00'):
            self.status = 'paid'
        elif self.amount_paid > Decimal('0.00'):
            self.status = 'partially_paid'

        self.save()

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name} ({self.currency} {self.total})"


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('1.00'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def line_total(self):
        return (self.quantity * self.unit_price).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.unit_price})"


class PaymentRecord(models.Model):
    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Wire / ACH'),
        ('stripe', 'Credit Card / Stripe'),
        ('paypal', 'PayPal'),
        ('wise', 'Wise Transfer'),
        ('cash_check', 'Cash or Check'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='bank_transfer')
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.invoice.currency} {self.amount} for {self.invoice.invoice_number}"

