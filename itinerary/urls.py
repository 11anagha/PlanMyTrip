from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path("generate_itinerary/", views.generate_itinerary, name="generate_itinerary")
]
