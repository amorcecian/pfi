from data_bike import app
from data_bike.computing_stations import new_station_number,get_stations
from flask import Flask, g, jsonify, request, render_template
from functools import wraps
import logging
import json
import pymssql
from config import config_data
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        valid_auth_header = "Bearer "+ config_data['API_TOKEN']
        # valid_auth_header = "Bearer "+ app.config['API_TOKEN']
        # valid_auth_header = app.config['API_TOKEN']
        if request.headers.get('Authorization') != valid_auth_header:
            print("Failed Auth!")
            ret = jsonify('Bad or no token.')
            return (ret, 403)
        else:
            print("Successful Auth")
            return f(*args, **kwargs)
    return decorated

def task_running(endpoint):
    @wraps(endpoint)
    def new_endpoint(*args, **kwargs):
        # with open('queue', 'r') as f:
        with open(os.path.join(__location__, 'queue'),'r') as f:
            status = f.read()
        if 'Pending' in status:
            return "Work is happenning. Please wait."
        else:
            return endpoint(*args, **kwargs)
    return new_endpoint

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

# @app.before_first_request
# def start():
#     engine = engine_creation()
#     df_merged_radius,df_stations = group_stations(engine)
#     print("Stations grouped successfully")
#     calculate_stations_usage(df_merged_radius,df_stations,engine)
#     return 'Data Successfully Loaded'

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    return response


@app.route('/')
@task_running
def hello():
    return 'Welcome to DataBike'

@app.route("/status")
@task_running
def status():
    return "Ready"

@app.route('/restart')
@task_running
# @requires_auth
def restart():
    with open(os.path.join(__location__, 'queue'),'w') as f:
        f.write("Pending,Start")
    return "System is restarting"
    # engine = engine_creation()
    # df_merged_radius,df_stations = group_stations(engine)
    # print("Stations grouped successfully")
    # calculate_stations_usage(df_merged_radius,df_stations,engine)
    # return 'Data Successfully Loaded'


@app.route('/add_station', methods=["POST"])
@requires_auth
def add_station_api():
    if request.method == 'POST':
        station = request.get_json()
        with open(os.path.join(__location__, 'queue'),'w') as f:
            f.write(f"Pending,Add_Station,{station['nombre']},{station['capacidad']},{station['cluster']}")
        station_number = new_station_number()
    return "Station " + str(station_number) + " is being added"
    #     engine = engine_creation()
    #     station = request.get_json()
    #     df_merged_radius,df_stations,station_number = add_station(station['nombre'],station['capacidad'],station['cluster'],engine)
    #     calculate_stations_usage(df_merged_radius,df_stations,engine)
    # return 'Station '+ station_number +' Added'

@app.route('/retrieve_stations')
def retrieve_stations():
    return get_stations()