from rest_framework import serializers

from .models import Link


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        exclude = ('dtm_created', 'dtm_updated')
        write_only_fields = ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content')
        read_only_fields = ('id', 'num_visits')
