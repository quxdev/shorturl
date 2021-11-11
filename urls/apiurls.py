from django.urls import path
from ..views.apiviews import *

app_name = 'qux_url_shortener_api'

urlpatterns = [
    path('new/', CreateShortLink.as_view(), name='new'),
]