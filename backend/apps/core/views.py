from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, Q

from apps.authentication.models import User
from apps.clients.models import Client
from apps.projects.models import Project, Deliverable, DeliverableVersion
from apps.tasks.models import Task
from apps.revisions.models import RevisionRequest
from apps.approvals.models import Approval
from apps.invoices.models import Invoice, InvoiceLineItem, PaymentRecord
from apps.notifications.models import Notification

def get_current_user(request):
    """Retrieves active user from session or defaults to Elena (Freelancer Lead)."""
    user_id = request.session.get('active_user_id')
    if user_id:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            pass
    return User.objects.filter(role='freelancer').first() or User.objects.first()

def switch_role(request, user_id):
    """Switch active user in session to test Freelancer, Client, or Team Member roles."""
    user = get_object_or_404(User, pk=user_id)
    request.session['active_user_id'] = user.id
    messages.success(request, f"Switched active view to {user.first_name} ({user.get_role_display()})")
    next_url = request.META.get('HTTP_REFERER') or '/dashboard/'
    return redirect(next_url)

def landing_page(request):
    """Public Website with Signature Sliced-Screen Hero."""
    demo_users = User.objects.all().order_by('id')
    projects = Project.objects.all().select_related('client')[:4]
    current_user = get_current_user(request)

    context = {
        'current_user': current_user,
        'demo_users': demo_users,
        'projects': projects,
    }
    return render(request, 'landing.html', context)

def dashboard_overview(request):
    """Main authenticated studio overview."""
    user = get_current_user(request)
    is_client = user.role == 'client'

    # Filter queryset by role
    project_qs = Project.objects.all().select_related('client')
    if is_client:
        project_qs = project_qs.filter(client__user=user)

    task_qs = Task.objects.all().select_related('project')
    if is_client:
        task_qs = task_qs.filter(project__client__user=user)

    invoice_qs = Invoice.objects.exclude(status='cancelled')
    if is_client:
        invoice_qs = invoice_qs.filter(client__user=user)

    total_invoiced = invoice_qs.aggregate(s=Sum('total'))['s'] or Decimal('0.00')
    total_paid = invoice_qs.aggregate(s=Sum('amount_paid'))['s'] or Decimal('0.00')
    outstanding = max(Decimal('0.00'), total_invoiced - total_paid)

    active_projects = project_qs.filter(status__in=['in_progress', 'in_review', 'changes_requested']).count()
    projects_in_review = project_qs.filter(status='in_review').count()
    pending_revisions = RevisionRequest.objects.filter(status__in=['submitted', 'in_review']).count()

    total_tasks = task_qs.count()
    done_tasks = task_qs.filter(status='done').count()
    completion_rate = round((done_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    recent_projects = project_qs[:4]
    recent_tasks = task_qs[:5]
    recent_invoices = invoice_qs[:3]
    demo_users = User.objects.all().order_by('id')

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': demo_users,
        'active_projects': active_projects,
        'projects_in_review': projects_in_review,
        'pending_revisions': pending_revisions,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'outstanding': outstanding,
        'completion_rate': completion_rate,
        'done_tasks': done_tasks,
        'total_tasks': total_tasks,
        'recent_projects': recent_projects,
        'recent_tasks': recent_tasks,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'dashboard/overview.html', context)

def clients_view(request):
    """Client Management CRUD."""
    user = get_current_user(request)
    if user.role == 'client':
        return redirect('/dashboard/')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            Client.objects.create(
                name=request.POST.get('name'),
                company_name=request.POST.get('company_name', ''),
                email=request.POST.get('email'),
                phone=request.POST.get('phone', ''),
                website=request.POST.get('website', ''),
                notes=request.POST.get('notes', ''),
                created_by=user,
            )
            messages.success(request, 'Client profile created successfully.')
        elif action == 'archive':
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, pk=client_id)
            client.is_archived = True
            client.save()
            messages.success(request, f'Client {client.name} archived safely.')
        return redirect('/dashboard/clients/')

    search_query = request.GET.get('search', '')
    clients_qs = Client.objects.filter(is_archived=False)
    if search_query:
        clients_qs = clients_qs.filter(
            Q(name__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'clients': clients_qs,
        'search_query': search_query,
    }
    return render(request, 'dashboard/clients.html', context)

def projects_view(request):
    """Project Portfolio & Creation."""
    user = get_current_user(request)

    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        client = get_object_or_404(Client, pk=client_id)
        project = Project.objects.create(
            name=request.POST.get('name'),
            client=client,
            owner=user,
            project_type=request.POST.get('project_type', 'UI/UX Design'),
            description=request.POST.get('description', ''),
            brief_content=request.POST.get('brief_content', ''),
            budget=Decimal(request.POST.get('budget', '0.00')),
            revision_allowance=int(request.POST.get('revision_allowance', 3)),
            due_date=request.POST.get('due_date') or None,
            status='in_progress',
        )
        messages.success(request, f"Project '{project.name}' created.")
        return redirect(f'/dashboard/projects/{project.id}/')

    status_filter = request.GET.get('status', 'all')
    project_qs = Project.objects.all().select_related('client')
    if user.role == 'client':
        project_qs = project_qs.filter(client__user=user)

    if status_filter != 'all':
        project_qs = project_qs.filter(status=status_filter)

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'projects': project_qs,
        'clients': Client.objects.filter(is_archived=False),
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/projects.html', context)

def project_detail_view(request, pk):
    """Multi-tab project workspace."""
    user = get_current_user(request)
    project = get_object_or_404(Project.objects.select_related('client'), pk=pk)

    # Handle Submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_task':
            Task.objects.create(
                project=project,
                title=request.POST.get('title'),
                priority=request.POST.get('priority', 'medium'),
                status='todo',
            )
            messages.success(request, 'Task added to sprint.')
        elif action == 'add_version':
            deliv_id = request.POST.get('deliverable_id')
            deliverable = get_object_or_404(Deliverable, pk=deliv_id)
            latest = deliverable.versions.order_by('-version_number').first()
            next_ver = (latest.version_number + 1) if latest else 1
            DeliverableVersion.objects.create(
                deliverable=deliverable,
                version_number=next_ver,
                file_name=request.POST.get('file_name', 'export.fig'),
                file_url='https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
                notes=request.POST.get('notes', ''),
                uploaded_by=user,
            )
            deliverable.status = 'in_review'
            deliverable.save()
            messages.success(request, f"Uploaded v{next_ver} for {deliverable.title}")
        elif action == 'submit_revision':
            # Check revision allowance in Python!
            used = project.revisions.filter(status__in=['in_progress', 'resolved', 'submitted']).count()
            if used >= project.revision_allowance:
                messages.error(request, f"Revision allowance exceeded ({used}/{project.revision_allowance} used). Contact studio for paid add-on scope.")
            else:
                deliv_id = request.POST.get('deliverable_id')
                deliverable = get_object_or_404(Deliverable, pk=deliv_id)
                RevisionRequest.objects.create(
                    project=project,
                    deliverable=deliverable,
                    requested_by=user,
                    description=request.POST.get('description'),
                    status='submitted',
                )
                deliverable.status = 'changes_requested'
                deliverable.save()
                messages.success(request, 'Revision request submitted and recorded against quota.')
        elif action == 'approve_version':
            ver_id = request.POST.get('version_id')
            version = get_object_or_404(DeliverableVersion, pk=ver_id)
            Approval.objects.create(
                version=version,
                decided_by=user,
                decision='approved',
                feedback=request.POST.get('feedback', 'Approved by client.'),
                client_signature=f"{user.first_name} {user.last_name}",
            )
            version.is_approved = True
            version.save()
            version.deliverable.status = 'approved'
            version.deliverable.save()
            messages.success(request, f"Official sign-off recorded for {version.deliverable.title} v{version.version_number}!")

        return redirect(f'/dashboard/projects/{project.id}/')

    tasks = project.tasks.all()
    deliverables = project.deliverables.prefetch_related('versions').all()
    revisions = project.revisions.all()
    approvals = Approval.objects.filter(version__deliverable__project=project)
    invoices = project.invoices.all()

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'project': project,
        'tasks': tasks,
        'deliverables': deliverables,
        'revisions': revisions,
        'approvals': approvals,
        'invoices': invoices,
    }
    return render(request, 'dashboard/project_detail.html', context)

def tasks_view(request):
    """Tasks & Kanban Drag and Drop."""
    user = get_current_user(request)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            project_id = request.POST.get('project_id')
            project = get_object_or_404(Project, pk=project_id)
            Task.objects.create(
                project=project,
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                priority=request.POST.get('priority', 'medium'),
                due_date=request.POST.get('due_date') or None,
                status='todo',
            )
            messages.success(request, 'Task created.')
            return redirect('/dashboard/tasks/')

    project_qs = Project.objects.all()
    task_qs = Task.objects.all().select_related('project')
    if user.role == 'client':
        task_qs = task_qs.filter(project__client__user=user)
        project_qs = project_qs.filter(client__user=user)

    tasks_todo = task_qs.filter(status='todo')
    tasks_progress = task_qs.filter(status='in_progress')
    tasks_review = task_qs.filter(status='in_review')
    tasks_done = task_qs.filter(status='done')

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'tasks': task_qs,
        'tasks_todo': tasks_todo,
        'tasks_progress': tasks_progress,
        'tasks_review': tasks_review,
        'tasks_done': tasks_done,
        'projects': project_qs,
    }
    return render(request, 'dashboard/tasks.html', context)

def update_task_status(request):
    """AJAX Drag-and-drop task status updater."""
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        status = request.POST.get('status')
        task = get_object_or_404(Task, pk=task_id)
        task.status = status
        if status == 'done':
            task.completed_at = timezone.now()
        task.save()
        return JsonResponse({'success': True, 'task_id': task.id, 'status': task.status})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def deliverables_view(request):
    """Deliverables and Version Management."""
    user = get_current_user(request)
    deliv_qs = Deliverable.objects.prefetch_related('versions').select_related('project')
    if user.role == 'client':
        deliv_qs = deliv_qs.filter(project__client__user=user)

    if request.method == 'POST':
        deliv_id = request.POST.get('deliverable_id')
        deliverable = get_object_or_404(Deliverable, pk=deliv_id)
        latest = deliverable.versions.order_by('-version_number').first()
        next_ver = (latest.version_number + 1) if latest else 1
        DeliverableVersion.objects.create(
            deliverable=deliverable,
            version_number=next_ver,
            file_name=request.POST.get('file_name', 'export.fig'),
            file_url='https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
            notes=request.POST.get('notes', ''),
            uploaded_by=user,
        )
        deliverable.status = 'in_review'
        deliverable.save()
        messages.success(request, f"Uploaded v{next_ver} for {deliverable.title}")
        return redirect('/dashboard/deliverables/')

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'deliverables': deliv_qs,
    }
    return render(request, 'dashboard/deliverables.html', context)

def revisions_view(request):
    """Revision Quota Tracker & Scope Enforcer."""
    user = get_current_user(request)
    rev_qs = RevisionRequest.objects.select_related('project', 'deliverable', 'requested_by')
    project_qs = Project.objects.all()

    if user.role == 'client':
        rev_qs = rev_qs.filter(project__client__user=user)
        project_qs = project_qs.filter(client__user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'resolve':
            rev_id = request.POST.get('revision_id')
            rev = get_object_or_404(RevisionRequest, pk=rev_id)
            rev.status = request.POST.get('status', 'resolved')
            rev.freelancer_response = request.POST.get('response', '')
            rev.resolved_at = timezone.now()
            rev.save()
            messages.success(request, f"Revision #{rev.id} updated.")
        return redirect('/dashboard/revisions/')

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'revisions': rev_qs,
        'projects': project_qs,
    }
    return render(request, 'dashboard/revisions.html', context)

def approvals_view(request):
    """Client Sign-offs and Approvals."""
    user = get_current_user(request)
    approval_qs = Approval.objects.select_related('version', 'decided_by', 'version__deliverable')
    if user.role == 'client':
        approval_qs = approval_qs.filter(version__deliverable__project__client__user=user)

    deliverables_pending = Deliverable.objects.filter(status='in_review').prefetch_related('versions')
    if user.role == 'client':
        deliverables_pending = deliverables_pending.filter(project__client__user=user)

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'approvals': approval_qs,
        'deliverables_pending': deliverables_pending,
    }
    return render(request, 'dashboard/approvals.html', context)

def invoices_view(request):
    """Invoicing, line items, and payment settlements."""
    user = get_current_user(request)
    invoice_qs = Invoice.objects.select_related('client', 'project')
    if user.role == 'client':
        invoice_qs = invoice_qs.filter(client__user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, pk=client_id)
            project_id = request.POST.get('project_id')
            project = Project.objects.filter(pk=project_id).first() if project_id else None

            inv = Invoice.objects.create(
                invoice_number=request.POST.get('invoice_number', f'INV-2026-{Invoice.objects.count()+101}'),
                client=client,
                project=project,
                issued_by=user,
                issue_date=request.POST.get('issue_date') or timezone.now().date(),
                due_date=request.POST.get('due_date') or timezone.now().date() + timezone.timedelta(days=14),
                tax_rate_percent=Decimal(request.POST.get('tax_rate', '0.00')),
                discount_amount=Decimal(request.POST.get('discount', '0.00')),
                notes=request.POST.get('notes', ''),
                status='sent',
            )

            # Add default line item
            desc = request.POST.get('item_description', 'Creative Milestone Services')
            qty = Decimal(request.POST.get('item_qty', '1.00'))
            price = Decimal(request.POST.get('item_price', '1500.00'))
            InvoiceLineItem.objects.create(
                invoice=inv,
                description=desc,
                quantity=qty,
                unit_price=price,
            )
            inv.calculate_totals()
            messages.success(request, f"Invoice {inv.invoice_number} created successfully.")
        elif action == 'record_payment':
            inv_id = request.POST.get('invoice_id')
            inv = get_object_or_404(Invoice, pk=inv_id)
            amt = Decimal(request.POST.get('amount', '0.00'))
            PaymentRecord.objects.create(
                invoice=inv,
                amount=amt,
                payment_method=request.POST.get('payment_method', 'bank_transfer'),
                payment_date=timezone.now().date(),
                reference_number=request.POST.get('reference', ''),
                recorded_by=user,
            )
            inv.amount_paid += amt
            if inv.amount_paid >= inv.total:
                inv.status = 'paid'
            else:
                inv.status = 'partially_paid'
            inv.save()
            messages.success(request, f"Payment of ${amt} recorded for {inv.invoice_number}.")

        return redirect('/dashboard/invoices/')

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'invoices': invoice_qs,
        'clients': Client.objects.filter(is_archived=False),
        'projects': Project.objects.all(),
    }
    return render(request, 'dashboard/invoices.html', context)

def reports_view(request):
    """Financial & Studio Velocity Analytics."""
    user = get_current_user(request)
    if user.role == 'client':
        return redirect('/dashboard/')

    invoice_qs = Invoice.objects.exclude(status='cancelled')
    total_invoiced = invoice_qs.aggregate(s=Sum('total'))['s'] or Decimal('0.00')
    total_paid = invoice_qs.aggregate(s=Sum('amount_paid'))['s'] or Decimal('0.00')
    outstanding = max(Decimal('0.00'), total_invoiced - total_paid)

    task_qs = Task.objects.all()
    total_tasks = task_qs.count()
    done_tasks = task_qs.filter(status='done').count()
    rate = round((done_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    projects = Project.objects.all()

    monthly_data = [
        {'month': 'May', 'revenue': 4200, 'invoiced': 5000},
        {'month': 'Jun', 'revenue': 6800, 'invoiced': 7200},
        {'month': 'Jul', 'revenue': 8400, 'invoiced': 9000},
        {'month': 'Aug', 'revenue': 11200, 'invoiced': 12500},
        {'month': 'Sep', 'revenue': 14800, 'invoiced': 16000},
        {'month': 'Oct', 'revenue': float(total_paid) if total_paid > 0 else 18500, 'invoiced': float(total_invoiced) if total_invoiced > 0 else 21000},
    ]

    context = {
        'current_user': user,
        'role': user.role,
        'demo_users': User.objects.all().order_by('id'),
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'outstanding': outstanding,
        'total_tasks': total_tasks,
        'done_tasks': done_tasks,
        'rate': rate,
        'projects': projects,
        'monthly_data': monthly_data,
    }
    return render(request, 'dashboard/reports.html', context)

