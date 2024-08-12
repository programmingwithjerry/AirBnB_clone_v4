#!/usr/bin/python3
""" 
Module for managing amenities associated with places.
"""
import os
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.amenity import Amenity
from models.place import Place
from flasgger.utils import swag_from


@app_views.route('/places/<string:place_id>/amenities', methods=['GET'], strict_slashes=False)
@swag_from('documentation/place_amenity/get_id.yml', methods=['GET'])
def list_amenities(place_id):
    """
    Retrieve all amenities linked to a specific place.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    amenities = [amenity.to_dict() for amenity in place.amenities]
    return jsonify(amenities)


@app_views.route('/places/<string:place_id>/amenities/<string:amenity_id>', methods=['DELETE'], strict_slashes=False)
@swag_from('documentation/place_amenity/delete.yml', methods=['DELETE'])
def remove_amenity(place_id, amenity_id):
    """
    Remove a specific amenity from a place.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404, description="Amenity not found")
    if amenity not in place.amenities:
        abort(404, description="Amenity not associated with this place")
    place.amenities.remove(amenity)
    storage.save()
    return jsonify({})


@app_views.route('/places/<string:place_id>/amenities/<string:amenity_id>', methods=['POST'], strict_slashes=False)
@swag_from('documentation/place_amenity/post.yml', methods=['POST'])
def add_amenity(place_id, amenity_id):
    """
    Add a specific amenity to a place.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404, description="Amenity not found")
    if amenity in place.amenities:
        return jsonify(amenity.to_dict()), 200
    place.amenities.append(amenity)
    storage.save()
    return jsonify(amenity.to_dict()), 201
