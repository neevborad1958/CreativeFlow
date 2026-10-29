from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Client
from .serializers import ClientSerializer
from apps.authentication.models import User

class ClientListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        
        # If user is a client, only show their own client record
        if user and getattr(user, 'role', None) == 'client':
            return Client.objects.filter(Q(user=user) | Q(email=user.email))
            
        queryset = Client.objects.all()
        archived = self.request.query_params.get('archived')
        search = self.request.query_params.get('search')
        
        if archived == 'true':
            queryset = queryset.filter(is_archived=True)
        else:
            queryset = queryset.filter(is_archived=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(created_by=user)


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def delete(self, request, *args, **kwargs):
        # Soft delete / archive to protect financial history
        client = self.get_object()
        client.is_archived = True
        client.save()
        return Response({'message': 'Client archived successfully', 'id': client.id})

