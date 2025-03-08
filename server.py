from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.message import EmailMessage
import os

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)  # Allow frontend requests

# ✅ Firebase Setup
cred = credentials.Certificate("config.json")  # Your Firebase Admin SDK JSON
firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Email Configuration (Change to your credentials)
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"

# ✅ Send Email Function
def send_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print("❌ Email Sending Failed:", e)
        return False

# ✅ API Route to Schedule an Appointment & Send Email
@app.route("/schedule_appointment", methods=["POST"])
def schedule_appointment():
    data = request.json
    buyer_id = data.get("buyer_id")
    buyer_name = data.get("buyer_name")
    seller_email = data.get("seller_email")
    seller_name = data.get("seller_name")
    property_type = data.get("property_type")
    property_price = data.get("property_price")

    if not (buyer_id and seller_email and property_type):
        return jsonify({"error": "Missing required fields"}), 400

    # Save to Firestore
    appointment_ref = db.collection("appointments").document()
    appointment_data = {
        "appointment_id": appointment_ref.id,
        "buyer_id": buyer_id,
        "buyer_name": buyer_name,
        "seller_email": seller_email,
        "seller_name": seller_name,
        "pro_type": property_type,
        "property_price": property_price,
        "status": "Pending"
    }
    appointment_ref.set(appointment_data)

    # Send Email to Seller
    subject = f"New Appointment Request for {property_type}"
    body = f"Hello {seller_name},\n\nYou have a new appointment request from {buyer_name} for your {property_type} listed at {property_price}.\nPlease respond as soon as possible.\n\nBest Regards,\nEstateBridge"
    
    if send_email(seller_email, subject, body):
        return jsonify({"message": "Appointment scheduled and email sent successfully!"}), 200
    else:
        return jsonify({"error": "Appointment saved, but email failed"}), 500

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
