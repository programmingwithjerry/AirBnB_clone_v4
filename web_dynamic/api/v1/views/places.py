#!/usr/bin/python3
"""
This module defines endpoints related to Place resources.
"""
from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.amenity import Amenity
from models.state import State
from flasgger.utils import swag_from


@app_views.route('/cities/<string:city_id>/places', methods=['GET'], strict_slashes=False)
@swag_from('documentation/places/get.yml', methods=['GET'])
def list_places_by_city(city_id):
    """
    Retrieve all places associated with a specific city ID.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404, description="City not found")
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<string:place_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/places/get_id.yml', methods=['GET'])
def retrieve_place(place_id):
    """
    Fetch a specific place by its ID.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    return jsonify(place.to_dict())


@app_views.route('/places/<string:place_id>', methods=['DELETE'], strict_slashes=False)
@swag_from('documentation/places/delete.yml', methods=['DELETE'])
def delete_place(place_id):
    """
    Delete a place based on its ID.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    place.delete()
    storage.save()
    return jsonify({})


@app_views.route('/cities/<string:city_id>/places', methods=['POST'], strict_slashes=False)
@swag_from('documentation/places/post.yml', methods=['POST'])
def create_place(city_id):
    """
    Create a new place within a specified city.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404, description="City not found")
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'user_id' not in request.get_json():
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    if 'name' not in request.get_json():
        return make_response(jsonify({"error": "Missing name"}), 400)

    place_data = request.get_json()
    place_data['city_id'] = city_id
    user = storage.get(User, place_data['user_id'])
    if user is None:
        abort(404, description="User not found")
    
    new_place = Place(**place_data)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<string:place_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/places/put.yml', methods=['PUT'])
def update_place(place_id):
    """
    Update the details of an existing place by its ID.
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    
    updates = request.get_json()
    for key, value in updates.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict())


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
@swag_from('documentation/places/search.yml', methods=['POST'])
def search_places():
    """
    Search for places based on criteria such as state IDs, city IDs, and amenities.
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    search_criteria = request.get_json()
    states = search_criteria.get('states', [])
    cities = search_criteria.get('cities', [])
    amenities = search_criteria.get('amenities', [])

    if not search_criteria or (not states and not cities and not amenities):
        places = storage.all(Place).values()
        all_places = [place.to_dict() for place in places]
        return jsonify(all_places)

    matched_places = []

    if states:
        state_objects = [storage.get(State, s_id) for s_id in states]
        for state in state_objects:
            if state:
                for city in state.cities:
                    if city:
                        matched_places.extend(city.places)

    if cities:
        city_objects = [storage.get(City, c_id) for c_id in cities]
        for city in city_objects:
            if city:
                for place in city.places:
                    if place not in matched_places:
                        matched_places.append(place)

    if amenities:
        if not matched_places:
            matched_places = storage.all(Place).values()
        amenity_objects = [storage.get(Amenity, a_id) for a_id in amenities]
        matched_places = [place for place in matched_places
                          if all(amenity in place.amenities
                                 for amenity in amenity_objects)]

    places_list = [place.to_dict() for place in matched_places]
    for place in places_list:
        place.pop('amenities', None)

    return jsonify(places_list)
