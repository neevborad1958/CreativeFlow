import os
from pathlib import Path
from django.http import HttpResponse
from django.conf import settings

def frontend_index(request):
    dist_index = settings.BASE_DIR.parent / 'frontend' / 'dist' / 'index.html'
    if dist_index.exists():
        with open(dist_index, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse("""
    <h1>CreativeFlow API is Running</h1>
    <p>API endpoints available at <a href="/api/v1/auth/me/">/api/v1/</a></p>
    <p>Frontend dev server runs at http://localhost:5173</p>
    """, content_type='text/html')

