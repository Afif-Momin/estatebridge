from flask import Blueprint, request, jsonify
from utils.db import db
from utils.email_service import send_email

appointment_routes = Blueprint("appointment_routes", __name__)

@appointment_routes.route("/book", methods=["POST"])
def book_appointment():
    try:
        data = request.json
        buyer_email = data["buyer_email"]
        seller_email = data["seller_email"]
        property_id = data["property_id"]
        appointment_time = data["appointment_time"]

        appointment_data = {
            "buyer_email": buyer_email,
            "seller_email": seller_email,
            "property_id": property_id,
            "appointment_time": appointment_time,
            "status": "pending"
        }

        db.collection("appointments").add(appointment_data)

        # Send confirmation email
        send_email(
            to_email=seller_email,
            subject="New Property Appointment Request",
            body=f"You have a new appointment request for property {property_id} at {appointment_time}."
        )

        return jsonify({"message": "Appointment booked successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

