import os

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User

# Create your views here.
def landing_page(request):
    return render(request, 'user/landing.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'user/register.html', {'form': form})

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
