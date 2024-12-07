from django.urls import path
from .views import ScrapeView, SearchView

urlpatterns = [
    path('scrape/', ScrapeView.as_view(), name='scrape'),
    path('search/', SearchView.as_view(), name='search'),
]