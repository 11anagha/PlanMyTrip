from django.urls import path
from . import views
from .views import generate_itinerary, download_itinerary_pdf
from .views import delete_itinerary

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path("download_itinerary/<int:itinerary_id>", views.download_itinerary_pdf, name="download_itinerary"),
    path("view-itinerary/<int:itinerary_id>/", views.view_itinerary, name="view_itinerary"),
    path("delete_itinerary/<int:itinerary_id>/", delete_itinerary, name="delete_itinerary"),
    path("itinerary/", views.itinerary, name="itinerary"),
]
