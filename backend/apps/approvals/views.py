from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from .models import Approval
from .serializers import ApprovalSerializer
from apps.projects.models import DeliverableVersion
from apps.authentication.models import User

class ApprovalListCreateView(generics.ListCreateAPIView):
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        queryset = Approval.objects.all().select_related('version', 'decided_by', 'version__deliverable')
        version_id = self.request.query_params.get('version')
        project_id = self.request.query_params.get('project')

        if version_id:
            queryset = queryset.filter(version_id=version_id)
        if project_id:
            queryset = queryset.filter(version__deliverable__project_id=project_id)

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        approval = serializer.save(decided_by=user)
        
        # Update DeliverableVersion and Deliverable statuses atomically
        version = approval.version
        deliverable = version.deliverable

        if approval.decision == 'approved':
            version.is_approved = True
            version.save()
            deliverable.status = 'approved'
            deliverable.save()
        elif approval.decision in ['changes_requested', 'rejected']:
            version.is_approved = False
            version.save()
            deliverable.status = 'changes_requested'
            deliverable.save()


class ApprovalDetailView(generics.RetrieveAPIView):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer

