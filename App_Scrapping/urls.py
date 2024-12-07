# from django.urls import path
# from .views import ScrapeView, SearchView

# urlpatterns = [
#     path('scrape/', ScrapeView.as_view(), name='scrape'),
#     path('search/', SearchView.as_view(), name='search'),
# ]

from django.urls import path
from .views import ScrapeView, SearchView, ScrapeWebsiteView, QueryDataView

urlpatterns = [
    path('scrape/', ScrapeView.as_view(), name='scrape'),
    path('search/', SearchView.as_view(), name='search'),
    path('scrape-data/', ScrapeWebsiteView.as_view(), name='scrape-website'),
    path('query/', QueryDataView.as_view(), name='query-data'),
]
