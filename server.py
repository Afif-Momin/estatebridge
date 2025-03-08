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
cred = credentials.Certificate("config.json")  # Ensure this file exists and is correct
firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Email Configuration (Use environment variables for security)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-app-password")

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

    # Get buyer and seller IDs
    buyer_id = data.get("buyer_id")
    seller_id = data.get("seller_id")
    pro_type = data.get("pro_type")
    property_price = data.get("property_price")

    # Validate required fields
    if not all([buyer_id, seller_id, pro_type, property_price]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # 🔍 Fetch Buyer Details from Firestore
        buyer_doc = db.collection("buyers").document(buyer_id).get()
        if not buyer_doc.exists:
            return jsonify({"error": "Buyer not found"}), 404
        buyer_data = buyer_doc.to_dict()
        buyer_name = buyer_data.get("buy_name")
        buyer_email = buyer_data.get("buy_email")

        # 🔍 Fetch Seller Details from Firestore
        seller_doc = db.collection("sellers").document(seller_id).get()
        if not seller_doc.exists:
            return jsonify({"error": "Seller not found"}), 404
        seller_data = seller_doc.to_dict()
        seller_name = seller_data.get("sell_name")
        seller_email = seller_data.get("sell_email")

        # ✅ Save to Firestore
        appointment_ref = db.collection("appointments").document()
        appointment_data = {
            "appointment_id": appointment_ref.id,
            "buyer_id": buyer_id,
            "buyer_name": buyer_name,
            "buyer_email": buyer_email,
            "seller_id": seller_id,
            "seller_name": seller_name,
            "seller_email": seller_email,
            "pro_type": pro_type,
            "property_price": property_price,
            "status": "Pending"
        }
        appointment_ref.set(appointment_data)

        # ✅ Send Email to Seller
        subject = f"New Appointment Request for {pro_type}"
        body = f"Hello {seller_name},\n\nYou have a new appointment request from {buyer_name} for your {pro_type} listed at {property_price}.\nPlease respond as soon as possible.\n\nBest Regards,\nEstateBridge"
        
        if send_email(seller_email, subject, body):
            return jsonify({"message": "Appointment scheduled and email sent successfully!"}), 200
        else:
            return jsonify({"error": "Appointment saved, but email failed"}), 500

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@app.route("/")
def home():
    return jsonify({"message": "EstateBridge Backend is Running!"}), 200


# ✅ Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
