from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests

class ScrapeForm(forms.Form):
    url = forms.URLField(
        label='',
        widget=forms.URLInput(attrs={
            'placeholder': 'Enter URL to scrape (e.g., https://example.com)',
            'class': 'form-control w-100',
            'required': 'required',
            'autofocus': 'autofocus',
        }),
        required=True,
        error_messages={
            'required': 'Please enter a URL.',
            'invalid': 'Please enter a valid URL (e.g., https://example.com).'
        },
        validators=[URLValidator(schemes=['http', 'https'])]
    )

    def clean_url(self):
        url = self.cleaned_data['url']
        try:
            headers = {'User-Agent': 'DjangoWebScraper/1.0'}
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                raise ValidationError('The URL is not accessible or returned an error.')
        except requests.RequestException:
            raise ValidationError('Unable to reach the URL. Please check the URL and try again.')
        return url