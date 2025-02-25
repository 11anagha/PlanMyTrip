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

        # ✅ Step 1: Validate form inputs
        if not all([current_location, destination, start_date, end_date, num_travelers, transport_mode]):
            return render(request, "itinerary/dashboard.html", {"error": "Please fill in all fields."})

        try:
            # ✅ Step 2: Convert dates and calculate duration
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            duration = (end_date_obj - start_date_obj).days

            if duration <= 0:
                return render(request, "itinerary/dashboard.html", {"error": "End date must be after start date."})

            # ✅ Debug: Print extracted inputs
            print(f"\n🔹 **User Input:** {current_location} → {destination}, {duration} days")
            print(f"👥 Travelers: {num_travelers}, 🚗 Mode: {transport_mode}\n")

        except ValueError:
            return render(request, "itinerary/dashboard.html", {"error": "Invalid date format."})

        # ✅ Step 3: Construct query
        query = (
            f"I want to travel from {current_location} to {destination}. The trip starts on {start_date} and ends on {end_date}, lasting {duration} days. "
            f"There are {num_travelers} travelers, and we will be traveling by {transport_mode}."
        )

        # ✅ Step 4: Initialize Gemini API Client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY is missing! Check environment variables.")
            return render(request, "itinerary/dashboard.html", {"error": "Internal error: Missing API key."})

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0,
                max_retries=2,
                api_key=api_key
            )

            prompt_template = PromptTemplate(
                input_variables=["query", "current_location", "destination", "start_date", "end_date", "duration", "num_travelers", "transport_mode"],
                template="""
                You are an AI travel assistant that generates structured travel itineraries in valid JSON format.

                ### **User Request:**  
                {query}

                ### **Instructions:**
                - Generate a structured, **realistic**, and **detailed** travel itinerary.
                - Organize the itinerary into **daily plans** including activities, dining, and transport.
                - Ensure the schedule is **balanced** with sightseeing, meals, travel time, rest breaks, and optional activities.
                - Mention local food spots, must-visit places, and cultural experiences.
                - If the journey involves multiple locations, include travel duration and suggested transport options.
                - Avoid unnecessary repetition and ensure time is utilized effectively.
                - Ensure output is **valid JSON**.

                ### **Response Format:**
                {{
                    "trip_details": {{
                        "current_location": "{current_location}",
                        "destination": "{destination}",
                        "start_date": "{start_date}",
                        "end_date": "{end_date}",
                        "duration": "{duration} days",
                        "num_travelers": "{num_travelers}",
                        "transport_mode": "{transport_mode}"
                    }},
                    "itinerary": {{
                        "Day 1": {{
                            "activities": [
                                "Explore a key landmark",
                                "Visit a cultural site",
                                "Try a local dining experience",
                                "Evening relaxation or optional activities"
                            ]
                        }},
                        "Day 2": {{
                            "activities": [
                                "Outdoor adventure",
                                "Shopping or market visit",
                                "Cultural or artistic experience"
                            ]
                        }}
                    }}
                }}
                """
            )

            chain = prompt_template | llm | JsonOutputParser()
            response = chain.invoke({
                "query": query,
                "current_location": current_location,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "duration": str(duration),  # Ensure it's a string
                "num_travelers": num_travelers,
                "transport_mode": transport_mode,
            })

            structured_response = response if response else {"itinerary": {}}

        except Exception as e:
            print(f"❌ Error generating itinerary: {str(e)}")
            structured_response = {"error": f"Failed to generate itinerary: {str(e)}"}


        # ✅ Step 6: Pass data to template
        return render(request, "itinerary/itinerary.html", {
            "response": structured_response,
            "trip_details": structured_response.get("trip_details", {}),  # ✅ Ensure trip details are passed
            "current_location": current_location,
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration,
            "num_travelers": num_travelers,
            "transport_mode": transport_mode,
        })

    return redirect("dashboard")  # Redirect if accessed via GET
