"""
Root URL Configuration for CreativeFlow Full-Stack Python Application.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core import views as core_views
from apps.invoices.views import InvoicePDFDownloadView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core Server-Rendered Views (Python over JSON)
    path('', core_views.landing_page, name='landing'),
    path('dashboard/', core_views.dashboard_overview, name='dashboard-overview'),
    path('dashboard/clients/', core_views.clients_view, name='dashboard-clients'),
    path('dashboard/projects/', core_views.projects_view, name='dashboard-projects'),
    path('dashboard/projects/<int:pk>/', core_views.project_detail_view, name='dashboard-project-detail'),
    path('dashboard/tasks/', core_views.tasks_view, name='dashboard-tasks'),
    path('dashboard/tasks/update-status/', core_views.update_task_status, name='dashboard-task-update-status'),
    path('dashboard/deliverables/', core_views.deliverables_view, name='dashboard-deliverables'),
    path('dashboard/revisions/', core_views.revisions_view, name='dashboard-revisions'),
    path('dashboard/approvals/', core_views.approvals_view, name='dashboard-approvals'),
    path('dashboard/invoices/', core_views.invoices_view, name='dashboard-invoices'),
    path('dashboard/reports/', core_views.reports_view, name='dashboard-reports'),

    # Role switch utility
    path('switch-role/<int:user_id>/', core_views.switch_role, name='switch-role'),

    # Direct ReportLab PDF Generation
    path('api/v1/invoices/<int:invoice_pk>/pdf/', InvoicePDFDownloadView.as_view(), name='invoice-pdf-download'),

    # REST APIs (kept for external or programmatic access)
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/clients/', include('apps.clients.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/files/', include('apps.files.urls')),
    path('api/v1/deliverables/', include('apps.projects.deliverable_urls')),
    path('api/v1/revisions/', include('apps.revisions.urls')),
    path('api/v1/approvals/', include('apps.approvals.urls')),
    path('api/v1/invoices/', include('apps.invoices.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
