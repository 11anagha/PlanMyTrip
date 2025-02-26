from django.urls import path
from . import views
from .views import generate_itinerary, download_itinerary_pdf
from .views import delete_itinerary

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path("generate_itinerary/", views.generate_itinerary, name="generate_itinerary"),
    path("download_itinerary/", views.download_itinerary_pdf, name="download_itinerary"),
    path("view-itinerary/<int:itinerary_id>/", views.view_itinerary, name="view_itinerary"),
    path("delete_itinerary/<int:itinerary_id>/", delete_itinerary, name="delete_itinerary"),
]
