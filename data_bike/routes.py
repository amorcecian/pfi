from data_bike import app
from data_bike.computing_stations import *
from flask import Flask, g, jsonify, request, render_template
from functools import wraps
import logging
import json
import pymssql

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        valid_auth_header = "Bearer "+ app.config['API_TOKEN']
        # valid_auth_header = app.config['API_TOKEN']
        if request.headers.get('Authorization') != valid_auth_header:
            print("Failed Auth!")
            ret = jsonify('Bad or no token.')
            return (ret, 403)
        else:
            print("Successful Auth")
            return f(*args, **kwargs)
    return decorated

def get_db(as_dict=False):
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'conn'):
        g.conn = pymssql.connect(
            server=app.config['SERVER'],
            db=app.config['DB'],
            user=app.config['USER'],
            password=app.config['PASSWORD'],
        )
    return g.conn

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'conn'):
        g.conn.close()


@app.route('/')
def hello():
    return 'Hello, world'


@app.route('/start', methods=["GET"])
def start():
    df_merged_radius,df_stations = group_stations()
    calculate_stations_usage(df_merged_radius,df_stations)
    return 'Data Successfully Loaded'

@app.route('/add_station', methods=["POST"])
def add_station_api():
    if request.method == 'POST':
        station = request.get_json()
        df_merged_radius,df_stations = add_station(station['nombre'],station['capacidad'],station['cluster'])
        calculate_stations_usage(df_merged_radius,df_stations)
    return 'Station Added'