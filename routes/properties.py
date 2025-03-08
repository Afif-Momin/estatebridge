from flask import Blueprint, request, jsonify
from utils.db import db

property_routes = Blueprint("property_routes", __name__)

@property_routes.route("/list", methods=["GET"])
def get_properties():
    try:
        properties_ref = db.collection("properties").stream()
        properties = [{**prop.to_dict(), "id": prop.id} for prop in properties_ref]
        return jsonify(properties), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

