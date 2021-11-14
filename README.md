# Qux ShortURL

## settings.py

Add `shortcut` to `INSTALLED_APPS`

## urls.py

```python
from django.urls import path, include
from shorturl.urls import appurls as shorturl_urls
from shorturl.urls import apiurls as shorturl_urls_api

urlpatterns += [
    path('', include(shorturl_urls, namespace='qux_shorturl')),
    path('api/v1/shorturl/', include(shorturl_urls_api, namespace='qux_shorturl_api')),
]
```

## URLS

### Application URLs

`/shorturl/`
- Name: `qux_shorturl:create` 
- View: `shorturl.views.appviews.LinkCreateView`

`/shorturl/list/`
- Name: `qux_shorturl:list`
- View: `shorturl.views.appviews.LinkListView`

### API URLs

`/api/v1/shorturl/new/` 
- Name: `qux_shorturl_api:new`
- View: `shorturl.views.apiviews.CreateShortLink`
