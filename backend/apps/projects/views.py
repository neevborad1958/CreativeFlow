from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Project, Deliverable, DeliverableVersion
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer,
    DeliverableSerializer, DeliverableVersionSerializer
)
from apps.authentication.models import User

class ProjectListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        queryset = Project.objects.all().select_related('client', 'owner')

        # Object-level security: clients only see their own projects
        if user and getattr(user, 'role', None) == 'client':
            queryset = queryset.filter(Q(client__user=user) | Q(client__email=user.email))
        elif user and getattr(user, 'role', None) == 'team_member':
            queryset = queryset.filter(Q(memberships__user=user) | Q(owner=user))

        status_param = self.request.query_params.get('status')
        client_param = self.request.query_params.get('client')
        search_param = self.request.query_params.get('search')

        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)
        if client_param:
            queryset = queryset.filter(client_id=client_param)
        if search_param:
            queryset = queryset.filter(
                Q(name__icontains=search_param) |
                Q(description__icontains=search_param) |
                Q(client__name__icontains=search_param)
            )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(owner=user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all().select_related('client', 'owner')
    serializer_class = ProjectDetailSerializer


class DeliverableListCreateView(generics.ListCreateAPIView):
    serializer_class = DeliverableSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        if project_id:
            return Deliverable.objects.filter(project_id=project_id)
        return Deliverable.objects.all()


class DeliverableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deliverable.objects.all()
    serializer_class = DeliverableSerializer


class DeliverableVersionCreateView(generics.CreateAPIView):
    serializer_class = DeliverableVersionSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        deliverable = serializer.validated_data['deliverable']
        latest_version = deliverable.versions.order_by('-version_number').first()
        next_ver = (latest_version.version_number + 1) if latest_version else 1
        
        # Mark deliverable back to In Review if new version uploaded
        deliverable.status = 'in_review'
        deliverable.save()
        
        serializer.save(
            uploaded_by=user,
            version_number=next_ver,
            is_approved=False
        )

