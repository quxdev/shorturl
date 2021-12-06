# Qux ShortURL

## settings.py

### INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...,
    'shorturl',
]
```

### DEFAULT_DOMAIN

This will be set to qux.dev if it is not set in settings.py

```python
DEFAULT_DOMAIN = 'domainname.com'
```

## urls.py

```
from shorturl.views.appviews import OpenOriginalLink
```

### Short URL management

```python
urlpatterns += [
    path('shorturl/', include('shorturl.urls.appurls')),
    path('api/v1/shorturl/', include('shorturl.urls.apiurls')),
]
```

### Using short URLs

This has to go LAST

```python
urlpatterns += [
    path('', OpenOriginalList.as_view(), name='open'),
]
```