from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

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

        request.session["itinerary_data"] = structured_response

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

@login_required
def download_itinerary_pdf(request):
    itinerary_data = request.session.get("itinerary_data")

    if not itinerary_data or not itinerary_data.get("itinerary"):
        return HttpResponse("No itinerary available. Please generate an itinerary first.", content_type="text/plain")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="itinerary.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # ✅ Title
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.darkblue,
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    elements.append(Paragraph("Travel Itinerary", title_style))

    # ✅ Trip Details (structured neatly)
    trip_details = itinerary_data.get("trip_details", {})
    trip_info = [
        ["From:", trip_details.get('current_location', 'N/A')],
        ["To:", trip_details.get('destination', 'N/A')],
        ["Dates:", f"{trip_details.get('start_date', 'N/A')} to {trip_details.get('end_date', 'N/A')}"],
        ["Duration:", trip_details.get('duration', 'N/A')],
        ["Travelers:", trip_details.get('num_travelers', 'N/A')],
        ["Transport:", trip_details.get('transport_mode', 'N/A')],
    ]

    table = Table(trip_info, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))

    elements.append(table)
    elements.append(Paragraph("<br/><br/>", styles["Normal"]))  # Space

    # ✅ Itinerary Details (formatted as a structured table)
    itinerary = itinerary_data.get("itinerary", {})
    itinerary_list = [["Day", "Activities"]]  # Table Header

    for day, details in itinerary.items():
        # **Text Wrapping: Makes Activities More Readable**
        activities = "<br/>".join(f"• {activity}" for activity in details.get("activities", []))
        itinerary_list.append([Paragraph(f"<b>{day}</b>", styles["BodyText"]), Paragraph(activities, styles["BodyText"])])

    itinerary_table = Table(itinerary_list, colWidths=[120, 380], repeatRows=1)
    itinerary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # **Align text to the top**
        ('LEFTPADDING', (0, 0), (-1, -1), 10),  # **More padding for spacing**
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(itinerary_table)

    # ✅ Build PDF
    doc.build(elements)

    return response