from decimal import Decimal
from rest_framework import serializers
from .models import Invoice, InvoiceLineItem, PaymentRecord

class InvoiceLineItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = InvoiceLineItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'line_total']


class PaymentRecordSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.ReadOnlyField(source='recorded_by.get_full_name')

    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'invoice', 'amount', 'payment_method', 'payment_date',
            'reference_number', 'notes', 'recorded_by', 'recorded_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.name')
    client_company = serializers.ReadOnlyField(source='client.company_name')
    project_name = serializers.ReadOnlyField(source='project.name')
    issued_by_name = serializers.ReadOnlyField(source='issued_by.get_full_name')
    items = InvoiceLineItemSerializer(many=True, required=False)
    payments = PaymentRecordSerializer(many=True, read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'client_name', 'client_company',
            'project', 'project_name', 'issued_by', 'issued_by_name',
            'issue_date', 'due_date', 'currency', 'subtotal',
            'tax_rate_percent', 'discount_amount', 'total', 'amount_paid',
            'balance_due', 'status', 'notes', 'terms', 'items', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'subtotal', 'total', 'amount_paid']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceLineItem.objects.create(invoice=invoice, **item_data)
        invoice.calculate_totals()
        return invoice

