from django.urls import path
from ..views.appviews import *

app_name = 'qux_url_shortener'

urlpatterns = [
    path('list/', LinkListView.as_view(), name='list'),
    path('', LinkCreateView.as_view(), name='create'),
]