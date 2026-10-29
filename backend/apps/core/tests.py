from django.test import TestCase, Client as DjangoClient
from apps.authentication.models import User
from apps.clients.models import Client
from apps.projects.models import Project, Deliverable, DeliverableVersion
from apps.tasks.models import Task
from apps.invoices.models import Invoice, InvoiceLineItem
from apps.revisions.models import RevisionRequest
from apps.approvals.models import Approval
from decimal import Decimal
from django.utils import timezone

class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = DjangoClient()
        self.freelancer = User.objects.create_user(
            username='elena_test',
            email='elena@test.com',
            first_name='Elena',
            last_name='Rostova',
            role='freelancer'
        )
        self.client_user = User.objects.create_user(
            username='marcus_test',
            email='marcus@test.com',
            first_name='Marcus',
            last_name='Vance',
            role='client'
        )
        self.biz_client = Client.objects.create(
            user=self.client_user,
            name='Marcus Vance',
            company_name='Lumina Labs',
            email='marcus@lumina.test'
        )
        self.project = Project.objects.create(
            name='Brand Identity',
            client=self.biz_client,
            owner=self.freelancer,
            budget=Decimal('12000.00'),
            revision_allowance=3,
            status='in_progress'
        )
        self.task = Task.objects.create(
            project=self.project,
            title='Initial Moodboard',
            status='todo'
        )
        self.deliv = Deliverable.objects.create(
            project=self.project,
            title='Logo Guidelines',
            status='in_review'
        )
        self.version = DeliverableVersion.objects.create(
            deliverable=self.deliv,
            version_number=1,
            file_name='guidelines-v1.pdf',
            file_url='https://example.com/file.pdf',
            uploaded_by=self.freelancer
        )
        self.invoice = Invoice.objects.create(
            invoice_number='INV-TEST-001',
            client=self.biz_client,
            project=self.project,
            issued_by=self.freelancer,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=14),
            total=Decimal('6000.00'),
            status='sent'
        )

    def test_landing_page(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'CreativeFlow')
        self.assertContains(res, 'slices-container')
        self.assertContains(res, 'studioCanvas')

    def test_dashboard_overview(self):
        res = self.client.get('/dashboard/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Studio Workspace')

    def test_clients_view(self):
        res = self.client.get('/dashboard/clients/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Lumina Labs')

    def test_projects_view(self):
        res = self.client.get('/dashboard/projects/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Brand Identity')

    def test_project_detail_view(self):
        res = self.client.get(f'/dashboard/projects/{self.project.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Brand Identity')
        self.assertContains(res, 'AGREED BUDGET')

    def test_tasks_view_and_update(self):
        res = self.client.get('/dashboard/tasks/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Initial Moodboard')

        # Test AJAX drag-and-drop status update
        post_res = self.client.post('/dashboard/tasks/update-status/', {
            'task_id': self.task.id,
            'status': 'done'
        })
        self.assertEqual(post_res.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')

    def test_deliverables_view(self):
        res = self.client.get('/dashboard/deliverables/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Logo Guidelines')
        self.assertContains(res, 'v1')

    def test_revisions_view(self):
        res = self.client.get('/dashboard/revisions/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Revision Quota Enforcer')

    def test_approvals_view(self):
        res = self.client.get('/dashboard/approvals/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Sign-Offs & Approvals')

    def test_invoices_view(self):
        res = self.client.get('/dashboard/invoices/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'INV-TEST-001')

    def test_reports_view(self):
        res = self.client.get('/dashboard/reports/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Reports & Analytics')

    def test_invoice_pdf_download(self):
        res = self.client.get(f'/api/v1/invoices/{self.invoice.id}/pdf/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertTrue(res.content.startswith(b'%PDF'))

    def test_role_switch(self):
        res = self.client.get(f'/switch-role/{self.client_user.id}/', follow=True)
        self.assertEqual(res.status_code, 200)
        session = self.client.session
        self.assertEqual(session.get('active_user_id'), self.client_user.id)
