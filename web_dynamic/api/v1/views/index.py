#!/usr/bin/python3
"""
This module defines endpoints related to the application's status
"""
from models import storage
from flask import Flask
from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status', strict_slashes=False)
def check_status():
    """
    Provide a JSON response indicating the application is running
    """
    return jsonify({"status": "OK"})


@app_views.route('/stats', strict_slashes=False)
def get_object_counts():
    """
    Provide a JSON response with counts of various object types
    """
    # Fetch and return the count of different object types from storage
    return jsonify({
        "amenities": storage.count("Amenity"),   # Count of amenities
        "cities": storage.count("City"),         # Count of cities
        "places": storage.count("Place"),       # Count of places
        "reviews": storage.count("Review"),     # Count of reviews
        "states": storage.count("State"),       # Count of states
        "users": storage.count("User")          # Count of users
    })
