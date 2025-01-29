from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
import os

@login_required
def dashboard(request):
    return render(request, 'itinerary/dashboard.html')

@login_required
def generate_itinerary(request):
    if request.method == "POST":
        departure = request.POST.get("departure")
        destination = request.POST.get("destination")
        duration = request.POST.get("duration")

        if not departure or not destination or not duration:
            return render(request, "itinerary/dashboard.html", {"error": "Please fill in all fields."})

        query = f"I want to go to {destination} from {departure} for {duration} day(s)."

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0,
                max_retries=2,
                api_key=os.environ.get("GEMINI_API_KEY")
            )

            prompt_template = f"""You are an intelligent AI assistant that generates travel itineraries based on user queries. User query: {query}"""
            prompt = PromptTemplate(
                input_variables=["query"],
                template=prompt_template
            )

            chain = prompt | llm | StrOutputParser()
            response = chain.invoke({"query": query})

        except Exception as e:
            response = f"Error generating itinerary: {str(e)}"

        context = {
            "response": response,
            "departure": departure,
            "destination": destination,
            "duration": duration
        }
        return render(request, "itinerary/itinerary.html", context)

    return redirect("dashboard")  # Redirect to dashboard if accessed via GET
