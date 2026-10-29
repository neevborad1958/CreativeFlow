from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.authentication.models import User
from apps.clients.models import Client
from apps.projects.models import Project, Deliverable, DeliverableVersion
from apps.tasks.models import Task
from apps.revisions.models import RevisionRequest
from apps.approvals.models import Approval
from apps.invoices.models import Invoice, InvoiceLineItem, PaymentRecord

class CreativeFlowCoreWorkflowTests(TestCase):
    def setUp(self):
        self.freelancer = User.objects.create_user(
            username='test_freelancer',
            email='free@test.com',
            password='password123',
            role='freelancer'
        )
        self.client_user = User.objects.create_user(
            username='test_client',
            email='client@test.com',
            password='password123',
            role='client'
        )
        self.client = Client.objects.create(
            name='Acme Corp',
            email='client@test.com',
            created_by=self.freelancer,
            user=self.client_user
        )
        self.project = Project.objects.create(
            name='Acme Rebrand',
            client=self.client,
            owner=self.freelancer,
            budget=Decimal('10000.00'),
            revision_allowance=2,
            status='in_progress'
        )

    def test_project_creation_and_membership(self):
        self.assertEqual(self.project.name, 'Acme Rebrand')
        self.assertEqual(self.project.budget, Decimal('10000.00'))
        self.assertEqual(self.project.revision_allowance, 2)

    def test_task_status_and_completion(self):
        task = Task.objects.create(
            project=self.project,
            title='Design Initial Moodboard',
            status='in_progress'
        )
        self.assertIsNone(task.completed_at)
        task.status = 'done'
        task.completed_at = timezone.now()
        task.save()
        self.assertIsNotNone(task.completed_at)

    def test_deliverable_version_and_approval(self):
        deliverable = Deliverable.objects.create(
            project=self.project,
            title='Brand Guide PDF',
            status='in_review'
        )
        version1 = DeliverableVersion.objects.create(
            deliverable=deliverable,
            version_number=1,
            file_url='https://example.com/guide_v1.pdf',
            file_name='guide_v1.pdf',
            uploaded_by=self.freelancer
        )
        self.assertFalse(version1.is_approved)

        # Client approves
        approval = Approval.objects.create(
            version=version1,
            decided_by=self.client_user,
            decision='approved',
            feedback='Approved without reservations.'
        )
        version1.is_approved = True
        version1.save()
        deliverable.status = 'approved'
        deliverable.save()

        self.assertTrue(version1.is_approved)
        self.assertEqual(deliverable.status, 'approved')
        self.assertEqual(approval.decision, 'approved')

    def test_revision_allowance_enforcement(self):
        deliverable = Deliverable.objects.create(
            project=self.project,
            title='Homepage Concept',
            status='in_review'
        )
        version1 = DeliverableVersion.objects.create(
            deliverable=deliverable,
            version_number=1,
            file_url='https://example.com/home_v1.png',
            file_name='home_v1.png'
        )

        # First revision
        RevisionRequest.objects.create(
            project=self.project,
            deliverable=deliverable,
            version=version1,
            requested_by=self.client_user,
            title='Revision 1',
            description='Make the logo slightly larger',
            status='resolved'
        )

        # Second revision (reaches allowance of 2)
        RevisionRequest.objects.create(
            project=self.project,
            deliverable=deliverable,
            version=version1,
            requested_by=self.client_user,
            title='Revision 2',
            description='Adjust footer background',
            status='in_progress'
        )

        active_revisions = self.project.revisions.filter(status__in=['in_progress', 'resolved']).count()
        self.assertEqual(active_revisions, 2)
        self.assertGreaterEqual(active_revisions, self.project.revision_allowance)

    def test_invoice_calculation_and_payment_records(self):
        invoice = Invoice.objects.create(
            invoice_number='INV-TEST-01',
            client=self.client,
            project=self.project,
            issued_by=self.freelancer,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=14),
            tax_rate_percent=Decimal('10.00'),
            discount_amount=Decimal('100.00')
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description='Design Direction',
            quantity=Decimal('2.00'),
            unit_price=Decimal('1000.00')
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description='Token System',
            quantity=Decimal('1.00'),
            unit_price=Decimal('500.00')
        )

        # Subtotal: 2500, Tax 10%: 250, Discount: 100 -> Total: 2650
        invoice.calculate_totals()
        self.assertEqual(invoice.subtotal, Decimal('2500.00'))
        self.assertEqual(invoice.total, Decimal('2650.00'))
        self.assertEqual(invoice.balance_due, Decimal('2650.00'))

        # Record partial payment of 1000
        PaymentRecord.objects.create(
            invoice=invoice,
            amount=Decimal('1000.00'),
            payment_date=timezone.now().date(),
            recorded_by=self.freelancer
        )
        invoice.amount_paid += Decimal('1000.00')
        invoice.status = 'partially_paid'
        invoice.save()

        self.assertEqual(invoice.amount_paid, Decimal('1000.00'))
        self.assertEqual(invoice.balance_due, Decimal('1650.00'))
        self.assertEqual(invoice.status, 'partially_paid')

        # Settle remaining 1650
        invoice.amount_paid += Decimal('1650.00')
        invoice.status = 'paid'
        invoice.save()

        self.assertEqual(invoice.balance_due, Decimal('0.00'))
        self.assertEqual(invoice.status, 'paid')

