from rest_framework import generics, parsers
from .models import ProjectFile
from .serializers import ProjectFileSerializer
from apps.authentication.models import User

class FileListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectFileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        if project_id:
            return ProjectFile.objects.filter(project_id=project_id)
        return ProjectFile.objects.all()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        file_obj = self.request.FILES.get('file')
        file_url = serializer.validated_data.get('file_url', '')
        file_size = serializer.validated_data.get('file_size_bytes', 0)
        file_type = serializer.validated_data.get('file_type', 'application/octet-stream')

        if file_obj:
            file_size = file_obj.size
            file_type = file_obj.content_type
            file_url = f"/media/project_files/{file_obj.name}"

        serializer.save(
            uploaded_by=user,
            file_size_bytes=file_size,
            file_type=file_type,
            file_url=file_url
        )


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer

