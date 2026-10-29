import io
from decimal import Decimal
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .models import Invoice, InvoiceLineItem, PaymentRecord
from .serializers import InvoiceSerializer, PaymentRecordSerializer
from apps.authentication.models import User

class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        queryset = Invoice.objects.all().select_related('client', 'project', 'issued_by').prefetch_related('items', 'payments')

        if user and getattr(user, 'role', None) == 'client':
            queryset = queryset.filter(client__user=user)

        client_id = self.request.query_params.get('client')
        project_id = self.request.query_params.get('project')
        status_param = self.request.query_params.get('status')

        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(issued_by=user)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.all().select_related('client', 'project').prefetch_related('items', 'payments')
    serializer_class = InvoiceSerializer

    def perform_update(self, serializer):
        invoice = serializer.save()
        invoice.calculate_totals()


class PaymentRecordCreateView(APIView):
    @transaction.atomic
    def post(self, request, invoice_pk):
        try:
            invoice = Invoice.objects.select_for_update().get(pk=invoice_pk)
        except Invoice.DoesNotExist:
            return Response({'detail': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

        amount = Decimal(str(request.data.get('amount', '0.00')))
        if amount <= Decimal('0.00'):
            return Response({'detail': 'Payment amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else User.objects.first()
        payment_date = request.data.get('payment_date', timezone.now().date().isoformat())
        payment_method = request.data.get('payment_method', 'bank_transfer')
        ref = request.data.get('reference_number', '')
        notes = request.data.get('notes', '')

        payment = PaymentRecord.objects.create(
            invoice=invoice,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=ref,
            notes=notes,
            recorded_by=user
        )

        invoice.amount_paid += amount
        if invoice.amount_paid >= invoice.total:
            invoice.status = 'paid'
        else:
            invoice.status = 'partially_paid'
        invoice.save()

        return Response({
            'message': 'Payment recorded successfully',
            'payment': PaymentRecordSerializer(payment).data,
            'invoice_status': invoice.status,
            'balance_due': str(invoice.balance_due)
        }, status=status.HTTP_201_CREATED)


class InvoicePDFDownloadView(APIView):
    def get(self, request, invoice_pk):
        try:
            invoice = Invoice.objects.select_related('client', 'issued_by').prefetch_related('items').get(pk=invoice_pk)
        except Invoice.DoesNotExist:
            return Response({'detail': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor('#20241E')
        forest_green = colors.HexColor('#52664D')
        cream_bg = colors.HexColor('#F8F4EC')
        text_dark = colors.HexColor('#1E201D')

        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=26,
            leading=30,
            textColor=primary_color,
            fontName='Helvetica-Bold'
        )

        meta_label = ParagraphStyle('MetaLabel', parent=styles['Normal'], fontSize=9, textColor=colors.gray)
        meta_value = ParagraphStyle('MetaVal', parent=styles['Normal'], fontSize=10, textColor=text_dark, fontName='Helvetica-Bold')

        elements = []

        # Header Table: Studio Branding vs Invoice Title
        header_data = [
            [
                Paragraph("<b>CREATIVEFLOW STUDIO</b><br/><font color='#52664D' size='9'>High-End Design & Motion Platform</font>", styles['Normal']),
                Paragraph(f"<b>INVOICE</b><br/><font color='#777777' size='11'>{invoice.invoice_number}</font>", title_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[320, 220])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # Billing and Details Table
        client_info = f"<b>Billed To:</b><br/>{invoice.client.name}<br/>{invoice.client.company_name}<br/>{invoice.client.email}"
        dates_info = f"<b>Issue Date:</b> {invoice.issue_date}<br/><b>Due Date:</b> {invoice.due_date}<br/><b>Status:</b> {invoice.get_status_display().upper()}"
        
        info_table = Table([[Paragraph(client_info, styles['Normal']), Paragraph(dates_info, styles['Normal'])]], colWidths=[320, 220])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cream_bg),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # Line Items Table
        items_data = [
            [
                Paragraph("<b>Description</b>", meta_value),
                Paragraph("<b>Qty</b>", meta_value),
                Paragraph(f"<b>Unit Price ({invoice.currency})</b>", meta_value),
                Paragraph(f"<b>Amount ({invoice.currency})</b>", meta_value)
            ]
        ]

        for item in invoice.items.all():
            items_data.append([
                Paragraph(item.description, styles['Normal']),
                Paragraph(str(item.quantity), styles['Normal']),
                Paragraph(f"{item.unit_price:.2f}", styles['Normal']),
                Paragraph(f"{item.line_total:.2f}", meta_value),
            ])

        if not invoice.items.exists():
            items_data.append([
                Paragraph("Standard Creative Services", styles['Normal']),
                Paragraph("1.00", styles['Normal']),
                Paragraph(f"{invoice.subtotal:.2f}", styles['Normal']),
                Paragraph(f"{invoice.subtotal:.2f}", meta_value),
            ])

        items_table = Table(items_data, colWidths=[260, 60, 110, 110])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), forest_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 15))

        # Totals Summary
        totals_data = [
            ['Subtotal:', f"{invoice.currency} {invoice.subtotal:.2f}"],
            ['Tax Rate:', f"{invoice.tax_rate_percent}%"],
            ['Discount:', f"- {invoice.currency} {invoice.discount_amount:.2f}"],
            ['Total Amount:', f"{invoice.currency} {invoice.total:.2f}"],
            ['Amount Paid:', f"- {invoice.currency} {invoice.amount_paid:.2f}"],
            ['Balance Due:', f"{invoice.currency} {invoice.balance_due:.2f}"],
        ]
        totals_table = Table(totals_data, colWidths=[150, 120], hAlign='RIGHT')
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, -1), (-1, -1), forest_green),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 25))

        # Notes & Payment Instructions
        notes_p = Paragraph(f"<b>Notes & Payment Terms:</b><br/>{invoice.notes}<br/>{invoice.terms}", styles['Normal'])
        elements.append(notes_p)

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
        return response

