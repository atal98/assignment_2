from django.urls import path
from .views import StartScrapingView, ScrapingStatusView, ScrapingStatusDownloadView

urlpatterns = [
    path('start_scraping/', StartScrapingView.as_view(), name='start_scraping'),
    path('scraping_status/<str:job_id>/', ScrapingStatusView.as_view(), name='scraping_status'),
    path('scraping_status_download/<str:job_id>/', ScrapingStatusDownloadView.as_view(), name='scraping_download_status'),
]
