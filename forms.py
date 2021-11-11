from django import forms

from .models import *


# custom widgets
class DateInput(forms.DateInput):
    input_type = 'date'


class LinkForm(forms.ModelForm):
    original_url = forms.URLField(
        required=True,
        label='URL',
        widget=forms.URLInput(attrs={
            'class': 'form-control foo-border',
            'placeholder': 'Enter URL'
        })
    )
    expiry_date = forms.DateField(
        required=False,
        label='Expiry Date',
        widget=DateInput(attrs={
            'class': 'form-control foo-border'
        })
    )

    class Meta:
        model = Link
        fields = ['original_url', 'expiry_date', ]

    def save(self, user=None):
        newform = super(LinkForm, self).save(commit=False)
        link_obj = Link.create_short_link(
            newform.original_url, newform.expiry_date
        )
        return link_obj
