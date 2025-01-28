import os

from django.shortcuts import render
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser

# Create your views here.
def landing_page(request):
    return render(request, 'user/landing.html')

otp_storage = {}  # Temporary storage for OTPs

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.is_active = False  # Deactivate until verified
            user.save()
            
            # Generate OTP and send via email
            otp = random.randint(100000, 999999)
            otp_storage[user.email] = otp
            
            send_mail(
                'Verify Your Email',
                f'Your OTP is {otp}',
                'your_email@gmail.com',  # Replace with your email
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Registration successful! Check your email for the OTP.')
            return redirect('verify_otp')
    else:
        form = RegisterForm()
    
    return render(request, 'user/register.html', {'form': form})



def verify_otp(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = int(request.POST['otp'])
        
        if otp_storage.get(email) == otp:
            user = User.objects.get(email=email)
            user.is_active = True  # Activate the user
            user.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
            otp_storage.pop(email, None)  # Clear OTP storage for this email
            return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'user/verify_otp.html')



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to the dashboard in the itinerary app
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'user/login.html', {'form': form})



def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing_page')  # Redirect to the landing page after logout


query = 'I want to go to trivandrum from kottayam in one day'

def generate_itinerary(request):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_retries=2,
        api_key=os.environ.get("GEMINI_API_KEY")
    )

    prompt_template = f"""You are an intelligent ai assistant that can generate travel itinerary and weather forecast based on the user query: {query}"""
    prompt = PromptTemplate(
        input_variables=["query"],
        template=prompt_template
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"query": query})
    context = {
        "response": response
    }
    return render(request, "user/itinerary.html", context)


