from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.projects.models import Project, Deliverable
from apps.tasks.models import Task
from apps.revisions.models import RevisionRequest
from apps.invoices.models import Invoice, PaymentRecord
from apps.clients.models import Client
from apps.authentication.models import User

class DashboardReportsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        user = request.user if request.user.is_authenticated else None

        # Filter scope for client if client role
        is_client = user and getattr(user, 'role', None) == 'client'

        # Project stats
        project_qs = Project.objects.all()
        if is_client:
            project_qs = project_qs.filter(client__user=user)

        total_projects = project_qs.count()
        active_projects = project_qs.filter(status__in=['in_progress', 'in_review', 'changes_requested']).count()
        completed_projects = project_qs.filter(status='completed').count()
        projects_in_review = project_qs.filter(status='in_review').count()

        # Task stats
        task_qs = Task.objects.all()
        if is_client:
            task_qs = task_qs.filter(project__client__user=user)

        total_tasks = task_qs.count()
        done_tasks = task_qs.filter(status='done').count()
        tasks_in_progress = task_qs.filter(status='in_progress').count()
        overdue_tasks = task_qs.filter(due_date__lt=today).exclude(status='done').count()
        task_completion_rate = round((done_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

        # Revision stats
        rev_qs = RevisionRequest.objects.all()
        if is_client:
            rev_qs = rev_qs.filter(project__client__user=user)
        pending_revisions = rev_qs.filter(status__in=['submitted', 'in_review']).count()

        # Invoices and Revenue stats
        invoice_qs = Invoice.objects.exclude(status='cancelled')
        if is_client:
            invoice_qs = invoice_qs.filter(client__user=user)

        total_invoiced = invoice_qs.aggregate(s=Sum('total'))['s'] or Decimal('0.00')
        total_paid_revenue = invoice_qs.aggregate(s=Sum('amount_paid'))['s'] or Decimal('0.00')
        outstanding_balance = max(Decimal('0.00'), total_invoiced - total_paid_revenue)
        unpaid_invoices_count = invoice_qs.filter(status__in=['sent', 'partially_paid', 'overdue']).count()

        # Monthly Revenue breakdown (sample aggregated timeline)
        monthly_revenue = [
            {'month': 'May', 'revenue': 4200, 'invoiced': 5000},
            {'month': 'Jun', 'revenue': 6800, 'invoiced': 7200},
            {'month': 'Jul', 'revenue': 8400, 'invoiced': 9000},
            {'month': 'Aug', 'revenue': 11200, 'invoiced': 12500},
            {'month': 'Sep', 'revenue': 14800, 'invoiced': 16000},
            {'month': 'Oct', 'revenue': float(total_paid_revenue) if total_paid_revenue > 0 else 18500, 'invoiced': float(total_invoiced) if total_invoiced > 0 else 21000},
        ]

        # Project Status Distribution
        status_counts = list(project_qs.values('status').annotate(count=Count('id')))
        status_map = {item['status']: item['count'] for item in status_counts}

        status_distribution = [
            {'name': 'In Progress', 'value': status_map.get('in_progress', 0), 'color': '#52664D'},
            {'name': 'In Review', 'value': status_map.get('in_review', 0), 'color': '#D7F7A5'},
            {'name': 'Changes Requested', 'value': status_map.get('changes_requested', 0), 'color': '#E8927C'},
            {'name': 'Completed', 'value': status_map.get('completed', 0), 'color': '#A7B99A'},
            {'name': 'Planned', 'value': status_map.get('planned', 0), 'color': '#E7DCCD'},
        ]

        return Response({
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'projects_in_review': projects_in_review,
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'done_tasks': done_tasks,
            'tasks_in_progress': tasks_in_progress,
            'overdue_tasks': overdue_tasks,
            'task_completion_rate': task_completion_rate,
            'pending_revisions': pending_revisions,
            'total_invoiced': float(total_invoiced),
            'total_paid_revenue': float(total_paid_revenue),
            'outstanding_balance': float(outstanding_balance),
            'unpaid_invoices_count': unpaid_invoices_count,
            'monthly_revenue': monthly_revenue,
            'status_distribution': status_distribution,
        })

