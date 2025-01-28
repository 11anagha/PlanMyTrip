from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login


# Create your views here.
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('user/login.html')  # Redirect to login if not authenticated
    return render(request, 'itinerary/dashboard.html')