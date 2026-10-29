from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.authentication.models import User, UserProfile
from apps.clients.models import Client
from apps.projects.models import Project, Deliverable, DeliverableVersion, ProjectMembership
from apps.tasks.models import Task, TaskComment
from apps.files.models import ProjectFile
from apps.revisions.models import RevisionRequest
from apps.approvals.models import Approval
from apps.invoices.models import Invoice, InvoiceLineItem, PaymentRecord
from apps.notifications.models import Notification, ActivityLog

class Command(BaseCommand):
    help = 'Seeds realistic demonstration data for CreativeFlow'

    def handle(self, *args, **options):
        self.stdout.write("Starting CreativeFlow demo database seeding...")

        today = timezone.now().date()

        # 1. Users
        admin_user, _ = User.objects.get_or_create(
            username='elena',
            defaults={
                'email': 'elena@creativeflow.studio',
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'role': 'freelancer',
                'title': 'Principal Creative Director & UI Architect',
                'company_name': 'Rostova Creative Lab',
                'hourly_rate': Decimal('145.00'),
                'bio': 'Award-winning creative director specializing in editorial typography, high-touch UI/UX, and 3D brand systems.',
                'avatar_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('creative123')
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user)

        client_user, _ = User.objects.get_or_create(
            username='marcus',
            defaults={
                'email': 'marcus@luminahealth.io',
                'first_name': 'Marcus',
                'last_name': 'Vance',
                'role': 'client',
                'title': 'VP of Brand & Growth',
                'company_name': 'Lumina Health Labs',
                'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80',
            }
        )
        client_user.set_password('client123')
        client_user.save()
        UserProfile.objects.get_or_create(user=client_user)

        team_user, _ = User.objects.get_or_create(
            username='sophia',
            defaults={
                'email': 'sophia@creativeflow.studio',
                'first_name': 'Sophia',
                'last_name': 'Chen',
                'role': 'team_member',
                'title': 'Senior 3D & Motion Designer',
                'company_name': 'Rostova Creative Lab',
                'hourly_rate': Decimal('110.00'),
                'avatar_url': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80',
            }
        )
        team_user.set_password('team123')
        team_user.save()
        UserProfile.objects.get_or_create(user=team_user)

        # 2. Clients
        client1, _ = Client.objects.get_or_create(
            email='marcus@luminahealth.io',
            defaults={
                'name': 'Marcus Vance',
                'company_name': 'Lumina Health Labs',
                'phone': '+1 (415) 882-9012',
                'website': 'https://luminahealth.io',
                'address': '550 Montgomery St, San Francisco, CA',
                'notes': 'High-growth biotechnology and digital therapeutics platform. Prefers sage green and clean editorial aesthetics.',
                'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80',
                'created_by': admin_user,
                'user': client_user,
            }
        )

        client2, _ = Client.objects.get_or_create(
            email='hina@kanso.jp',
            defaults={
                'name': 'Hina Takahashi',
                'company_name': 'Kanso Architectural Objects',
                'phone': '+81 3 5555 0192',
                'website': 'https://kanso-objects.jp',
                'address': 'Minato City, Tokyo, Japan',
                'notes': 'Japanese architectural furniture and objects. Values minimalism, natural materials, and subtle micro-interactions.',
                'avatar_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80',
                'created_by': admin_user,
            }
        )

        client3, _ = Client.objects.get_or_create(
            email='julian@velvetoak.coffee',
            defaults={
                'name': 'Julian Vance',
                'company_name': 'Velvet & Oak Roastery',
                'phone': '+1 (503) 712-4491',
                'website': 'https://velvetandoak.coffee',
                'address': 'Pearl District, Portland, OR',
                'notes': 'Single-origin artisanal roastery launching tactile foil packaging and 3D web experience.',
                'avatar_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80',
                'created_by': admin_user,
            }
        )

        client4, _ = Client.objects.get_or_create(
            email='sarah.lin@apexrobotics.ai',
            defaults={
                'name': 'Dr. Sarah Lin',
                'company_name': 'Apex Industrial Robotics',
                'phone': '+1 (617) 940-1123',
                'website': 'https://apexrobotics.ai',
                'address': 'Kendall Square, Cambridge, MA',
                'notes': 'Autonomous warehouse robotics requiring 3D product renders and Series B keynote presentation deck.',
                'avatar_url': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80',
                'created_by': admin_user,
            }
        )

        # 3. Projects
        p1, _ = Project.objects.get_or_create(
            name='Lumina Health Digital Platform & Design System',
            defaults={
                'client': client1,
                'owner': admin_user,
                'project_type': 'UI/UX Design',
                'status': 'in_progress',
                'priority': 'high',
                'budget': Decimal('18500.00'),
                'currency': 'USD',
                'revision_allowance': 3,
                'start_date': today - timedelta(days=18),
                'due_date': today + timedelta(days=12),
                'description': 'End-to-end design of Lumina patient diagnostic portal, design token architecture, and interactive widget component library.',
                'brief_content': 'Create a high-trust, calming clinical interface using muted sages, warm cream backgrounds, and clear visual hierarchy for blood biomarker reports.',
                'cover_image_url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80',
            }
        )

        p2, _ = Project.objects.get_or_create(
            name='Kanso Minimalist E-Commerce Experience',
            defaults={
                'client': client2,
                'owner': admin_user,
                'project_type': 'Web Design & Dev',
                'status': 'in_review',
                'priority': 'medium',
                'budget': Decimal('24000.00'),
                'currency': 'USD',
                'revision_allowance': 2,
                'start_date': today - timedelta(days=35),
                'due_date': today + timedelta(days=5),
                'description': 'Editorial bespoke storefront highlighting handcrafted wooden and ceramic interior pieces.',
                'cover_image_url': 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80',
            }
        )

        p3, _ = Project.objects.get_or_create(
            name='Velvet & Oak Tactile Packaging & 3D Spatial Renders',
            defaults={
                'client': client3,
                'owner': admin_user,
                'project_type': '3D & Motion',
                'status': 'in_progress',
                'priority': 'urgent',
                'budget': Decimal('9800.00'),
                'currency': 'USD',
                'revision_allowance': 3,
                'start_date': today - timedelta(days=10),
                'due_date': today + timedelta(days=8),
                'description': 'Custom matte box packaging with embossed gold foil details and 3D interactive web viewer models.',
                'cover_image_url': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80',
            }
        )

        p4, _ = Project.objects.get_or_create(
            name='Apex Robotics Series-B Keynote & Brand Reveal',
            defaults={
                'client': client4,
                'owner': admin_user,
                'project_type': 'Video Production',
                'status': 'completed',
                'priority': 'medium',
                'budget': Decimal('14500.00'),
                'currency': 'USD',
                'revision_allowance': 2,
                'start_date': today - timedelta(days=60),
                'due_date': today - timedelta(days=10),
                'description': 'Cinematic 90-second product render video and 45-slide investor pitch presentation deck.',
                'cover_image_url': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80',
            }
        )

        # 4. Deliverables & Versions
        d1, _ = Deliverable.objects.get_or_create(
            project=p1,
            title='Patient Diagnostic Dashboard UI (Figma Specs)',
            defaults={
                'format_type': 'Figma',
                'status': 'in_review',
                'description': 'Responsive desktop & tablet layouts with interactive state animations for diagnostic results.'
            }
        )

        DeliverableVersion.objects.get_or_create(
            deliverable=d1,
            version_number=1,
            defaults={
                'file_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
                'file_name': 'Lumina_Portal_v1_Wireframes.fig',
                'file_size_bytes': 14200000,
                'file_type': 'application/x-figma',
                'notes': 'Initial layout structure and color system explorations.',
                'uploaded_by': admin_user,
            }
        )

        dv2, _ = DeliverableVersion.objects.get_or_create(
            deliverable=d1,
            version_number=2,
            defaults={
                'file_url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80',
                'file_name': 'Lumina_Portal_v2_HighFidelity.fig',
                'file_size_bytes': 28600000,
                'file_type': 'application/x-figma',
                'notes': 'Incorporated client feedback on biomarker graph contrast and simplified top navigation.',
                'uploaded_by': admin_user,
                'is_approved': False,
            }
        )

        d2, _ = Deliverable.objects.get_or_create(
            project=p1,
            title='Brand Guidelines & Typography Spec Sheet',
            defaults={
                'format_type': 'PDF',
                'status': 'approved',
                'description': 'Complete guidelines covering editorial typography, logo clearspace, and digital color tokens.'
            }
        )

        dv_guide, _ = DeliverableVersion.objects.get_or_create(
            deliverable=d2,
            version_number=1,
            defaults={
                'file_url': 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80',
                'file_name': 'Lumina_Brand_Guidelines_v1.0.pdf',
                'file_size_bytes': 18500000,
                'file_type': 'application/pdf',
                'notes': 'Final approved typography and color token documentation.',
                'is_final': True,
                'is_approved': True,
                'uploaded_by': admin_user,
            }
        )

        Approval.objects.get_or_create(
            version=dv_guide,
            decided_by=client_user,
            defaults={
                'decision': 'approved',
                'feedback': 'Exceptional aesthetic balance. The sage green palette and serif typography are aligned with our clinical brand vision.',
                'client_signature': 'Marcus Vance, VP Brand',
            }
        )

        # 5. Revision Requests
        RevisionRequest.objects.get_or_create(
            project=p1,
            deliverable=d1,
            version=dv2,
            defaults={
                'requested_by': client_user,
                'title': 'Biomarker card contrast and mobile tab spacing',
                'description': 'Could we increase the contrast on the secondary health metrics pills and adjust the mobile tab bar margin by 8px?',
                'status': 'in_progress',
                'freelancer_response': 'Adjusted token variables and added higher-contrast accessible borders. Preparing updated Figma component preview.',
            }
        )

        # 6. Tasks
        tasks_data = [
            {'p': p1, 'title': 'Design blood biomarker trend chart component', 'status': 'done', 'priority': 'high', 'due': today - timedelta(days=2), 'assignee': admin_user},
            {'p': p1, 'title': 'Build interactive prototype for doctor referral flow', 'status': 'in_progress', 'priority': 'urgent', 'due': today + timedelta(days=3), 'assignee': admin_user},
            {'p': p1, 'title': 'Generate dark mode color token definitions', 'status': 'todo', 'priority': 'medium', 'due': today + timedelta(days=8), 'assignee': team_user},
            {'p': p1, 'title': 'Client review of revised diagnostic portal layouts', 'status': 'in_review', 'priority': 'high', 'due': today + timedelta(days=2), 'assignee': admin_user},
            {'p': p2, 'title': 'Configure Shopify Liquid product grid templates', 'status': 'done', 'priority': 'high', 'due': today - timedelta(days=5), 'assignee': team_user},
            {'p': p2, 'title': 'Test checkout funnel responsive micro-interactions', 'status': 'in_progress', 'priority': 'urgent', 'due': today + timedelta(days=1), 'assignee': admin_user},
            {'p': p3, 'title': 'Model 3D coffee bag packaging in Blender', 'status': 'done', 'priority': 'high', 'due': today - timedelta(days=3), 'assignee': team_user},
            {'p': p3, 'title': 'Render foil embossing light passes for web viewer', 'status': 'in_progress', 'priority': 'high', 'due': today + timedelta(days=4), 'assignee': team_user},
            {'p': p4, 'title': 'Deliver final 4K ProRes investor video export', 'status': 'done', 'priority': 'medium', 'due': today - timedelta(days=12), 'assignee': team_user},
        ]

        for idx, t in enumerate(tasks_data):
            Task.objects.get_or_create(
                project=t['p'],
                title=t['title'],
                defaults={
                    'status': t['status'],
                    'priority': t['priority'],
                    'due_date': t['due'],
                    'assignee': t['assignee'],
                    'order_index': idx,
                    'completed_at': timezone.now() if t['status'] == 'done' else None,
                }
            )

        # 7. Invoices & Payments
        inv1, _ = Invoice.objects.get_or_create(
            invoice_number='INV-2026-001',
            defaults={
                'client': client1,
                'project': p1,
                'issued_by': admin_user,
                'issue_date': today - timedelta(days=15),
                'due_date': today + timedelta(days=5),
                'currency': 'USD',
                'subtotal': Decimal('9250.00'),
                'tax_rate_percent': Decimal('8.50'),
                'discount_amount': Decimal('0.00'),
                'total': Decimal('10036.25'),
                'amount_paid': Decimal('5000.00'),
                'status': 'partially_paid',
                'notes': 'Phase 1 Milestone Invoice: Brand identity, design system tokens, and UI layout wireframes.',
            }
        )

        InvoiceLineItem.objects.get_or_create(
            invoice=inv1,
            description='Brand Identity & Design System Token Architecture',
            defaults={'quantity': Decimal('1.00'), 'unit_price': Decimal('5500.00')}
        )
        InvoiceLineItem.objects.get_or_create(
            invoice=inv1,
            description='Patient Diagnostic Dashboard UI Design (Wireframes & Figma Assets)',
            defaults={'quantity': Decimal('1.00'), 'unit_price': Decimal('3750.00')}
        )

        PaymentRecord.objects.get_or_create(
            invoice=inv1,
            reference_number='WIRE-LUMINA-8812',
            defaults={
                'amount': Decimal('5000.00'),
                'payment_method': 'bank_transfer',
                'payment_date': today - timedelta(days=10),
                'notes': '50% Initial Project Deposit received via ACH wire.',
                'recorded_by': admin_user,
            }
        )

        inv2, _ = Invoice.objects.get_or_create(
            invoice_number='INV-2026-002',
            defaults={
                'client': client2,
                'project': p2,
                'issued_by': admin_user,
                'issue_date': today - timedelta(days=25),
                'due_date': today - timedelta(days=5),
                'currency': 'USD',
                'subtotal': Decimal('12000.00'),
                'tax_rate_percent': Decimal('0.00'),
                'discount_amount': Decimal('500.00'),
                'total': Decimal('11500.00'),
                'amount_paid': Decimal('11500.00'),
                'status': 'paid',
                'notes': 'Kanso Storefront Phase 1 milestone payment - Full amount settled.',
            }
        )

        InvoiceLineItem.objects.get_or_create(
            invoice=inv2,
            description='E-Commerce Architecture & Custom Theme Development',
            defaults={'quantity': Decimal('1.00'), 'unit_price': Decimal('12000.00')}
        )

        PaymentRecord.objects.get_or_create(
            invoice=inv2,
            reference_number='STRIPE-CH-9941',
            defaults={
                'amount': Decimal('11500.00'),
                'payment_method': 'stripe',
                'payment_date': today - timedelta(days=12),
                'notes': 'Full settlement processed via Stripe.',
                'recorded_by': admin_user,
            }
        )

        # 8. Notifications & Activities
        Notification.objects.get_or_create(
            recipient=admin_user,
            title='Revision Submitted by Marcus Vance',
            defaults={
                'message': 'Marcus submitted a revision request for Patient Diagnostic Dashboard UI (v2).',
                'notification_type': 'revision',
                'link': '/dashboard/revisions',
                'is_read': False,
            }
        )

        Notification.objects.get_or_create(
            recipient=admin_user,
            title='Payment Received: $5,000.00',
            defaults={
                'message': 'Wire transfer received for Invoice INV-2026-001 (Lumina Health Labs).',
                'notification_type': 'payment',
                'link': '/dashboard/invoices',
                'is_read': True,
            }
        )

        ActivityLog.objects.get_or_create(
            user=admin_user,
            action='uploaded_deliverable',
            target_type='DeliverableVersion',
            target_id=dv2.id,
            defaults={'description': 'Uploaded v2 of Patient Diagnostic Dashboard UI (Figma Specs)'}
        )

        ActivityLog.objects.get_or_create(
            user=client_user,
            action='approved_deliverable',
            target_type='DeliverableVersion',
            target_id=dv_guide.id,
            defaults={'description': 'Marcus Vance approved Brand Guidelines & Typography Spec Sheet'}
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded CreativeFlow with comprehensive studio data!'))

