from rest_framework import authentication
from rest_framework import exceptions
from .models import User

class HeaderUserAuthentication(authentication.BaseAuthentication):
    """
    Allows authentication via:
    1. 'X-User-Id' header containing a user ID or username.
    2. 'Authorization: Bearer <user_id_or_token>'
    Falls back gracefully if no header is provided.
    """
    def authenticate(self, request):
        user_id = request.headers.get('X-User-Id')
        auth_header = request.headers.get('Authorization')

        if not user_id and auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1].strip()
            if token.isdigit():
                user_id = token

        if not user_id:
            # Let other authenticators (e.g. SessionAuthentication) handle it
            return None

        try:
            if str(user_id).isdigit():
                user = User.objects.get(pk=int(user_id))
            else:
                user = User.objects.get(username=user_id)
            return (user, None)
        except User.DoesNotExist:
            return None

