from django.urls import path
from . import views
from .views import generate_itinerary, download_itinerary_pdf

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path("generate_itinerary/", views.generate_itinerary, name="generate_itinerary"),
    path("download-itinerary/", views.download_itinerary_pdf, name="download_itinerary"),
]
