from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', wordgod_view, name='wordgod_view'),
    path('upload_for_study/', for_study, name='for_study'),
    path('upload_for_exam/', for_exam, name='for_exam'),
    path('upload_for_text_study/', for_text_study, name='for_text_study'),
    path('upload_for_sentence_study/', for_sentence_study, name='for_sentence_study'),
    path('upload_for_meaning_study/', for_meaning_study, name='for_meaning_study')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)