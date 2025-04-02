import json
import os
from httpcore import request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from itinerary.models import Itinerary
from langchain_mistralai import ChatMistralAI

def generate_itinerary(current_user, current_location, destination, start_date, end_date, num_travelers, transport_mode):
    query =f"""I want to travel from {current_location} to {destination}. The trip starts on {start_date} and ends on {end_date}.
    There are {num_travelers} travelers, and we will be traveling by {transport_mode}."""

    mistral_api_key = os.environ.get("MISTRAL_API_KEY")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")


    try:
        # llm = ChatMistralAI(
        #     model="mistral-large-latest",
        #     temperature=0,
        #     max_retries=2,
        #     api_key=mistral_api_key
        # )

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=gemini_api_key
        )

        prompt_template = PromptTemplate(
            input_variables=["query", "current_location", "destination", "start_date", "end_date", "num_travelers", "transport_mode"],
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
            "num_travelers": num_travelers,
            "transport_mode": transport_mode,
        })

        # ✅ Save itinerary to the database
        Itinerary.objects.create(
            user=current_user,
            current_location=current_location,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            num_travelers=num_travelers,
            transport_mode=transport_mode,
            itinerary_data=json.dumps(response)
        )

    except Exception as e:
        print(f"❌ Error generating itinerary: {str(e)}")