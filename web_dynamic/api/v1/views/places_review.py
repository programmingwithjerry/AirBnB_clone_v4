#!/usr/bin/python3
"""
Module for managing reviews within the application.
"""
from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.place import Place
from models.review import Review
from models.user import User
from flasgger.utils import swag_from


@app_views.route('/places/<string:place_id>/reviews', methods=['GET'], strict_slashes=False)
@swag_from('documentation/reviews/get.yml', methods=['GET'])
def list_reviews(place_id):
    """
    Retrieve all reviews associated with a specific place.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    reviews = [review.to_dict() for review in place.reviews]
    return jsonify(reviews)


@app_views.route('/reviews/<string:review_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/reviews/get_id.yml', methods=['GET'])
def retrieve_review(review_id):
    """
    Retrieve a review by its unique ID.
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404, description="Review not found")
    return jsonify(review.to_dict())


@app_views.route('/reviews/<string:review_id>', methods=['DELETE'], strict_slashes=False)
@swag_from('documentation/reviews/delete.yml', methods=['DELETE'])
def remove_review(review_id):
    """
    Delete a review based on its unique ID.
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404, description="Review not found")
    review.delete()
    storage.save()
    return jsonify({})


@app_views.route('/places/<string:place_id>/reviews', methods=['POST'], strict_slashes=False)
@swag_from('documentation/reviews/post.yml', methods=['POST'])
def create_review(place_id):
    """
    Create a new review for a specific place.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, description="Place not found")
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'user_id' not in request.get_json():
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    if 'text' not in request.get_json():
        return make_response(jsonify({"error": "Missing text"}), 400)
    data = request.get_json()
    data['place_id'] = place_id
    user = storage.get(User, data['user_id'])
    if user is None:
        abort(404, description="User not found")
    review = Review(**data)
    review.save()
    return jsonify(review.to_dict()), 201


@app_views.route('/reviews/<string:review_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/reviews/put.yml', methods=['PUT'])
def update_review(review_id):
    """
    Update an existing review based on its unique ID.
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    review = storage.get(Review, review_id)
    if review is None:
        abort(404, description="Review not found")
    for key, value in request.get_json().items():
        if key not in ['id', 'user_id', 'place_id', 'created_at', 'updated']:
            setattr(review, key, value)
    storage.save()
    return jsonify(review.to_dict())
