#!/usr/bin/python3
""" Initializes a Flash Web Application """
from models import storage
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from os import environ
from flask import Flask, render_template
import uuid


app = Flask(__name__)


@app.teardown_appcontext
def close_database_session(error):
    """ Close the current SQLAlchemy Session """
    storage.close()


@app.route('/0-hbnb/', strict_slashes=False)
def display_hbnb():
    """ Display the HBNB home page """
    all_states = storage.all(State).values()
    sorted_states = sorted(all_states, key=lambda s: s.name)
    state_city_list = []

    for state in sorted_states:
        state_city_list.append([state, sorted(state.cities, key=lambda c: c.name)])

    all_amenities = storage.all(Amenity).values()
    sorted_amenities = sorted(all_amenities, key=lambda a: a.name)

    all_places = storage.all(Place).values()
    sorted_places = sorted(all_places, key=lambda p: p.name)

    return render_template('0-hbnb.html',
                           states=state_city_list,
                           amenities=sorted_amenities,
                           places=sorted_places,
                           cache_id=uuid.uuid4())


if __name__ == "__main__":
    """ Run the application """
    app.run(host='0.0.0.0', port=5001)
