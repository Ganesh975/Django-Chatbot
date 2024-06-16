from django.urls import path
from .views import home, send_message, upload_image,send_audio,fetch_language

urlpatterns = [
    path('', home, name='home'),
    path('send_message/', send_message, name='send_message'),
    path('upload_image/', upload_image, name='upload_image'),
    path('send_audio/', send_audio, name='send_audio'),
    path('fetch_language/', fetch_language, name='fetch_language'),
]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)