from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
import os


# Create your views here.
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('user/login.html')  # Redirect to login if not authenticated
    return render(request, 'itinerary/dashboard.html')

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
    return render(request, "itinerary/itinerary.html", context)
