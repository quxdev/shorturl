from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from ..serializers import *


class OpenOriginalLink(TemplateView):
    """
    valid url https://domain.io/short_url_code

    GET /a1B2c3
    """
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def get(request, shorturl: str = None, **kwargs):
        if shorturl is None:
            raise Http404

        print(shorturl)
        original_url = Link.get_original_url(request, shorturl)

        if original_url is None:
            raise Http404

        return HttpResponseRedirect(original_url)


class LinkCreateView(TemplateView):
    template_name = 'qux_shorturl_create.html'


class LinkViewSet(ModelViewSet):
    model = Link
    queryset = Link.objects.none().order_by('id')
    serializer_class = LinkSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LinkListView(ListView):
    model = Link
    queryset = Link.objects.all().order_by('-id')
    fields = ['original_url', 'short_url', 'num_visits', 'domain', 'expiry_date', ]
    template_name = 'qux_shorturl_list.html'
    permission_classes = (permissions.AllowAny,)
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return super().get(request, *args, **kwargs)
        else:
            return redirect(reverse('qux_shorturl:create'))
