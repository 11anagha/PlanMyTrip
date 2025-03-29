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
import json  # If storing details as JSON
from .models import Itinerary
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .generate_itinerary import generate_itinerary

@login_required
def dashboard(request):
    if request.method == "POST":
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        destination = request.POST["destination"]
        current_location = request.POST["current_location"]
        num_travelers = request.POST["num_travelers"]
        transport_mode = request.POST["transport_mode"]
        today = datetime.now()
    
        if start_date < str(today):
            messages.warning(request, "Please enter a valid date")
            return redirect("dashboard")
        else:
            current_user = request.user
            generate_itinerary(current_user=current_user, start_date=start_date, end_date=end_date, destination=destination, current_location=current_location, num_travelers=num_travelers,
                               transport_mode=transport_mode)
            return redirect("itinerary")
        
    itineraries = Itinerary.objects.filter(user=request.user).order_by("-created_at")
            
    return render(request, "itinerary/dashboard.html", {"itineraries": itineraries})

   
@login_required
def download_itinerary_pdf(request, itinerary_id):
    # Fetch itinerary data from the database
    itinerary_instance = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
    
    # Ensure itinerary_data is parsed correctly
    if isinstance(itinerary_instance.itinerary_data, str):  # If stored as JSON string, parse it
        itinerary_data = json.loads(itinerary_instance.itinerary_data)
    else:  # If already a dictionary, use it directly
        itinerary_data = itinerary_instance.itinerary_data

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
        fontSize=20,
        textColor=colors.darkblue,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    elements.append(Paragraph("Travel Itinerary", title_style))

    # ✅ Trip Details
    trip_details = itinerary_data.get("trip_details", {})
    trip_info = [
        ["From:", trip_details.get('current_location', 'N/A')],
        ["To:", trip_details.get('destination', 'N/A')],
        ["Dates:", f"{trip_details.get('start_date', 'N/A')} to {trip_details.get('end_date', 'N/A')}"],
        ["Travelers:", trip_details.get('num_travelers', 'N/A')],
        ["Transport:", trip_details.get('transport_mode', 'N/A')],
    ]

    table = Table(trip_info, colWidths=[120, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))

    elements.append(table)
    elements.append(Paragraph("<br/><br/>", styles["Normal"]))  # Space

    # ✅ Itinerary Details
    itinerary = itinerary_data.get("itinerary", {})
    itinerary_list = [["Day", "Activities"]]  # Table Header

    for day, details in itinerary.items():
        activities = "<br/>".join(f"• {act['time']}: {act['activity']}" for act in details.get("activities", []))
        itinerary_list.append([Paragraph(f"<b>{day}</b>", styles["BodyText"]), Paragraph(activities, styles["BodyText"])])

    itinerary_table = Table(itinerary_list, colWidths=[120, 380], repeatRows=1)
    itinerary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(itinerary_table)

    # ✅ Build PDF
    doc.build(elements)

    return response


@login_required
def view_itinerary(request, itinerary_id):
    try:
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)

        # ✅ Ensure itinerary_data is parsed correctly
        if isinstance(itinerary.itinerary_data, str):  # If stored as JSON string, parse it
            itinerary_data = json.loads(itinerary.itinerary_data)
        else:  # If already a dictionary, use it directly
            itinerary_data = itinerary.itinerary_data

        trip_details = itinerary_data.get("trip_details", {})
        itinerary_days = itinerary_data.get("itinerary", {})

    except Itinerary.DoesNotExist:
        messages.error(request, "Itinerary not found.")
        return redirect("dashboard")

    return render(request, "itinerary/itinerary_details.html", {
        "trip_details": trip_details,
        "itinerary_id": itinerary_id,
        "itinerary": itinerary_days  # ✅ Pass parsed itinerary data
    })

@login_required
def delete_itinerary(request, itinerary_id):
    itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
    itinerary.delete()
    messages.success(request, "Itinerary deleted successfully.")
    return redirect("dashboard")  # Redirect back to the dashboard


@login_required
def itinerary(request):
    trip_instance = Itinerary.objects.filter(user=request.user).last()
    
    if trip_instance:
        # ✅ Ensure itinerary_data is parsed correctly
        if isinstance(trip_instance.itinerary_data, str):  # If stored as JSON string, parse it
            itinerary_data = json.loads(trip_instance.itinerary_data)
        else:  # If already a dictionary, use it directly
            itinerary_data = trip_instance.itinerary_data

        trip_details = itinerary_data.get("trip_details", {})
        itinerary = itinerary_data.get("itinerary", {})
    else:
        trip_details = {}
        itinerary = {}

    return render(request, "itinerary/itinerary.html", {
        "trip_details": trip_details,
        "itinerary": itinerary,
        "trip_instance": trip_instance
    })