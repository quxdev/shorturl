from django.contrib import admin

from qux.models import CoreModelAdmin
from .models import *


class LinkAdmin(CoreModelAdmin):
    list_display = ('id', 'num_visits', 'original_url', 'short_url', 'expiry_date', 'domain',) \
                   + CoreModelAdmin.list_display
    search_fields = ('id', 'num_visits', 'original_url')


admin.site.register(Link, LinkAdmin)


class TrackingVisitAdmin(CoreModelAdmin):
    list_display = ('id', 'link', 'user', 'request_url', 'http_referer',) \
                   + CoreModelAdmin.list_display
    search_fields = ('id', 'link__original_url', 'link__short_url', 'user__username', 'request_url', 'http_referer')
    raw_id_fields = ('link', 'user',)


admin.site.register(TrackingVisit, TrackingVisitAdmin)
