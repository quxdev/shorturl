from django.urls import path
from ..views.appviews import *

app_name = 'shorturl'

urlpatterns = [
    path('shorturl/list/', LinkListView.as_view(), name='list'),
    path('shorturl/', LinkCreateView.as_view(), name='create'),
    path('<str:shorturl>/', OpenOriginalLink.as_view(), name='open')
]
