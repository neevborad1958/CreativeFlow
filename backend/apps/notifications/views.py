from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification, ActivityLog
from .serializers import NotificationSerializer, ActivityLogSerializer
from apps.authentication.models import User

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            user = User.objects.first()
        if user:
            return Notification.objects.filter(recipient=user)
        return Notification.objects.none()


class NotificationMarkReadView(APIView):
    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk)
            notif.is_read = True
            notif.save()
            return Response({'status': 'marked as read'})
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


class NotificationMarkAllReadView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else User.objects.first()
        if user:
            Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})


class ActivityLogListView(generics.ListAPIView):
    queryset = ActivityLog.objects.all().select_related('user')[:30]
    serializer_class = ActivityLogSerializer

