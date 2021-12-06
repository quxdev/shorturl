import random
import string
from urllib import parse

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone

from qux.models import CoreModel

CHAR256 = {
    'max_length': 256,
    'default': None,
    'null': True,
    'blank': True
}

dnb = dict(
    default=None,
    null=True,
    blank=True
)

DEFAULT_DOMAIN = getattr(settings, 'DEFAULT_DOMAIN', 'qux.dev')


class Link(CoreModel):
    # Using this field is actually a Charfield but with a URL validator. AWESOME!
    original_url = models.URLField(max_length=2048, verbose_name='URL')
    short_url = models.CharField(
        max_length=16, unique=True, default=None, null=True,
        verbose_name='Short URL'
    )
    num_visits = models.IntegerField(default=0)
    domain = models.CharField(max_length=64, default=DEFAULT_DOMAIN)
    expiry_date = models.DateField(default=None, null=True, blank=True)
    # UTM fields for analytics
    utm_source = models.CharField(**CHAR256)
    utm_medium = models.CharField(**CHAR256)
    utm_campaign = models.CharField(**CHAR256)
    utm_content = models.CharField(**CHAR256)
    utm_term = models.CharField(**CHAR256)

    def save(self, *args, **kwargs):
        # pk = self.pk
        try:
            super(self.__class__, self).save(*args, **kwargs)
        except:
            return 

        if self.short_url is None:
            self.short_url = self.__class__.generate_short_url()
            result = self.save()
        else:
            if Link.objects.filter(short_url=self.short_url).exists():
                return
            else:
                result = self.save()          
        return result

    def __str__(self):
        return '%s : %s' % (self.id, self.original_url)

    def get_short_url(self):
        return self.domain + self.short_url

    @staticmethod
    def generate_short_url():
        """
        Generate short_url for original_url.

        - Recursion here could end up being a bad idea.
        ? Consider replacing with a while loop

        :return:
        """
        characters = string.digits + string.ascii_letters
        short_url = ''.join([random.choice(characters) for _ in range(6)])

        # short_url exists. Try again.
        if Link.objects.filter(short_url=short_url).exists():
            return Link.generate_short_url()

        return short_url

    @staticmethod
    def create_short_link(original_url, shorturl, expiry_date=None, domain=None):
        """
        Encodes original url and returns short url

        :param original_url:
        :param shorturl:
        :param domain:
        :param expiry_date:
        :return:
        """
        domain = domain if domain else settings.DEFAULT_DOMAIN

        filterparams = dict(
            original_url=original_url,
            domain=domain
        )
        linkobj = None
        if shorturl:
            if Link.objects.filter(short_url=shorturl).exists():
                filterparams.update({'short_url': shorturl})
                linkobj = Link.objects.filter(**filterparams).last()
                if not linkobj:
                    return
                else:
                    filterparams.update({'short_url': shorturl})
        else: 
            linkobj = Link.objects.filter(**filterparams).last()
        if linkobj is None:
            linkobj, _ = Link.objects.get_or_create(**filterparams)

            # We do this to extract and store utm params
            params = dict(parse.parse_qsl(parse.urlsplit(original_url).query))
            for key, value in params.items():
                setattr(linkobj, key, value)
            linkobj.save()

        if expiry_date:
            linkobj.expiry_date = expiry_date
            linkobj.save()

        return linkobj

    @staticmethod
    def get_original_url(request, slug):
        """
        Decodes short url and returns original url

        :param request:
        :param slug:
        :return:
        """
        dtmstamp = timezone.now().date()
        print(f"dtmstamp = {dtmstamp}")
        linkobj = Link.objects.filter(short_url=slug)\
            .filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=dtmstamp))\
            .last()
        TrackingVisit.create(request, linkobj)

        # short_url not found
        if not linkobj:
            return None

        # short_url found
        # Increment usage counter and return lookup
        linkobj.num_visits += 1
        linkobj.save()
        return linkobj.original_url


class LinkVisit(CoreModel):
    request_url = models.URLField(
        max_length=1024,
        verbose_name='Request URL'
    )

    # request.META
    http_accept_language = models.CharField(
        max_length=256, **dnb,
        verbose_name='HTTP Language'
    )
    http_user_agent = models.CharField(
        max_length=512, **dnb,
        verbose_name='HTTP UserAgent'
    )
    http_referer = models.URLField(
        max_length=1024, **dnb,
        verbose_name='HTTP Referer'
    )
    remote_addr = models.CharField(
        max_length=256, **dnb,
        verbose_name='Remote Address'
    )
    remote_port = models.CharField(
        max_length=256, **dnb,
        verbose_name='Remote Port'
    )
    server_name = models.CharField(
        max_length=256, **dnb,
        verbose_name='Server Name'
    )
    server_port = models.CharField(
        max_length=256, **dnb,
        verbose_name='Server Port'
    )
    http_host = models.URLField(
        max_length=1024, **dnb,
        verbose_name='HTTP Host'
    )
    query_string = models.URLField(
        max_length=1024, **dnb,
        verbose_name='Query String'
    )

    get_params = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True

    @staticmethod
    def store_data(request, track_obj=None):
        metadata = ['HTTP_ACCEPT_LANGUAGE', 'HTTP_USER_AGENT', 'HTTP_REFERER', 'REMOTE_ADDR',
                    'REMOTE_PORT', 'SERVER_NAME', 'SERVER_PORT', 'HTTP_HOST', 'QUERY_STRING']
        
        [setattr(track_obj, k.lower(), request.META.get(k, None))
         for k in metadata]

        track_obj.get_params.update(request.GET.dict())
        track_obj.save()

        return track_obj


class TrackingVisit(LinkVisit):
    user = models.ForeignKey(User, on_delete=models.CASCADE, **dnb)
    link = models.ForeignKey(Link, on_delete=models.CASCADE, **dnb)

    class Meta:
        verbose_name = 'Tracking Visit'
        verbose_name_plural = 'Tracking Visits'

    @staticmethod
    def create(request, linkobj=None):
        """
        To create Tracking Visits
        :param request:
        :param linkobj:
        :return:
        """
        user = None
        if request.user.is_authenticated:
            user = request.user

        request_url = request.build_absolute_uri()
        track_obj = TrackingVisit.objects.create(
            request_url=request_url,
            user=user,
            link=linkobj,
        )

        track_obj = LinkVisit.store_data(request, track_obj)
        return track_obj
