from django.conf import settings
from django.http.response import HttpResponse
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Link


class CreateShortLink(APIView):
    """
    valid url /api/shorturl/new/

    POST Parameters -\n
        {
            "original_url": "https://www.google.com/"
        }
            OR
        {
            "original_url": "https://www.google.com/",
            # optional
            "domain": "ggl.io",
            # option
            "expiry_date": "2021-01-19"
        }

    Returns -\n
        {
            "short_url": "domain.io/a1B2c3"
        }
    """
    model = Link
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request):
        data = request.data
        original_url = data.get('original_url', None)
        custom_url = data.get('custom_url', None)
        expiry_date = data.get('expiry_date', None)
        domain = data.get('domain', None)

        click_from = request.META.get('HTTP_REFERER', None)
        is_valid_req = request.user.is_authenticated

        if settings.DEBUG:
            # is_valid_req = is_valid_req or '127.0.0.1' in click_from
            is_valid_req = True

        is_valid_req = is_valid_req or 'domain.io' in click_from

        if not is_valid_req:
            return HttpResponse('Unauthorized', status=401)

        json_data = {}
        if original_url:
            link_obj = Link.create_short_link(original_url, custom_url, expiry_date, domain)
            if link_obj:
                json_data["short_url"] = link_obj.get_short_url()
            else:
                json_data["message"] = "This url is already take, please try a different one!"

        return Response(json_data)
