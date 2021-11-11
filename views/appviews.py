from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from ..models import Link
from ..serializers import *


class LinkViewSet(ModelViewSet):
    model = Link
    queryset = Link.objects.none().order_by('id')
    serializer_class = LinkSerializer
    permission_classes = (permissions.IsAuthenticated,)


class OpenOriginalLink(View):
    """
    valid url https://domain.io/short_url_code

    GET /a1B2c3
    """
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def get(request, short_url):
        
        original_url = Link.get_original_url(request, short_url)

        if original_url is None:
            raise Http404

        return HttpResponseRedirect(original_url)


class LinkListView(ListView):
    model = Link
    queryset = Link.objects.all()
    template_name = 'qux_url_shortener_list.html'
    paginate_by = 25
    permission_classes = (permissions.AllowAny,)
    fields = ['original_url', 'short_url', 'num_visits', 'domain', 'expiry_date', ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['canonical'] = reverse('shorturl:list')
        return context

    def get_queryset(self):
        queryset = Link.objects.all().order_by('-id')
        return queryset

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return redirect(reverse('qux_url_shortener:create'))

        return super(ListView, self).get(request, *args, **kwargs)


class LinkCreateView(View):
    template_name = 'qux_url_shortener_create.html'

    def get(self, request):
        context = {}       
        return render(request, self.template_name, context)
