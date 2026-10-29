from rest_framework import generics, status
from rest_framework.response import Response
from django.utils import timezone
from .models import RevisionRequest
from .serializers import RevisionRequestSerializer
from apps.projects.models import Project
from apps.authentication.models import User

class RevisionListCreateView(generics.ListCreateAPIView):
    serializer_class = RevisionRequestSerializer

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        queryset = RevisionRequest.objects.all().select_related('project', 'deliverable', 'version', 'requested_by')
        
        project_id = self.request.query_params.get('project')
        status_param = self.request.query_params.get('status')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)
            
        return queryset

    def create(self, request, *args, **kwargs):
        project_id = request.data.get('project')
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        # Count active/consumed revisions
        used_revisions = project.revisions.filter(status__in=['in_progress', 'resolved', 'submitted']).count()
        if used_revisions >= project.revision_allowance:
            return Response({
                'detail': f'Revision allowance exceeded ({used_revisions}/{project.revision_allowance} used). Please contact freelancer to discuss additional revision scope.',
                'allowance_exceeded': True,
                'used': used_revisions,
                'allowance': project.revision_allowance
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        rev = serializer.save(requested_by=user)
        # Update deliverable status to Changes Requested
        if rev.deliverable:
            rev.deliverable.status = 'changes_requested'
            rev.deliverable.save()


class RevisionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RevisionRequest.objects.all()
    serializer_class = RevisionRequestSerializer

    def perform_update(self, serializer):
        status_val = serializer.validated_data.get('status')
        if status_val == 'resolved':
            serializer.save(resolved_at=timezone.now())
        else:
            serializer.save()

