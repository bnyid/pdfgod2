from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', wordgod_view, name='wordgod_view'),
    path('upload_for_study/', for_study, name='for_study'),
    path('upload_for_exam/', for_exam, name='for_exam'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)