from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
from datetime import datetime

@login_required
def dashboard(request):
    return render(request, 'itinerary/dashboard.html')

@login_required
def generate_itinerary(request):
    if request.method == "POST":
        current_location = request.POST.get("current_location")
        destination = request.POST.get("destination")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        num_travelers = request.POST.get("num_travelers")
        transport_mode = request.POST.get("transport_mode")

        if not all([current_location, destination, start_date, end_date, num_travelers, transport_mode]):
            return render(request, "itinerary/dashboard.html", {"error": "Please fill in all fields."})

        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end_date_obj - start_date_obj).days

        query = (
            f"I want to travel from {current_location} to {destination}. The trip starts on {start_date} and ends on {end_date}, lasting {duration} days. "
            f"There are {num_travelers} travelers, and we will be traveling by {transport_mode}."
        )

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0,
                max_retries=2,
                api_key=os.environ.get("GEMINI_API_KEY")
            )

            prompt_template = """
                You are an intelligent AI assistant that generates structured travel itineraries in valid JSON format.

                User query: {query}

                Response format:
                {{
                    "Day 1": ["Activity 1", "Activity 2"],
                    "Day 2": ["Activity 1", "Activity 2"]
                }}

                Ensure that the output is a valid JSON object and contains no extra text.
            """

            prompt = PromptTemplate(
                input_variables=["query"],
                template=prompt_template
            )

            chain = prompt | llm | JsonOutputParser()
            response = chain.invoke({"query": query})

            print("Raw LLM Response:", response)  # Debugging: See what Gemini returns

            structured_response = response  # No need for json.loads()

        except Exception as e:
            structured_response = {"Error": [f"Error generating itinerary: {str(e)}"]}

        context = {
            "response": structured_response,
            "current_location": current_location,
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration,
            "num_travelers": num_travelers,
            "transport_mode": transport_mode,
        }
        return render(request, "itinerary/itinerary.html", context)

    return redirect("dashboard")  # Redirect to dashboard if accessed via GET
