from django.urls import path
from ..views.apiviews import *

app_name = 'shorturl_api'

urlpatterns = [
    path('new/', CreateShortLink.as_view(), name='new'),
]