from data_bike import app
from data_bike.computing_stations import new_station_number,get_stations,get_clusters
from flask import Flask, g, jsonify, request, render_template
from functools import wraps
import logging
import json
import pymssql
from data_bike.aadservice import getaccesstoken
from data_bike.pbiembedservice import getembedparam
from data_bike.config import config_data
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
    return str(station_number)
    #     engine = engine_creation()
    #     station = request.get_json()
    #     df_merged_radius,df_stations,station_number = add_station(station['nombre'],station['capacidad'],station['cluster'],engine)
    #     calculate_stations_usage(df_merged_radius,df_stations,engine)
    # return 'Station '+ station_number +' Added'

@app.route('/retrieve_stations')
def retrieve_stations():
    engine = engine_creation()
    return get_stations(engine)

@app.route('/')
def login():
    '''Returns a static HTML page'''

    return render_template('authentication-login.html')

@app.route('/home')
def home():
    '''Returns a static HTML page'''

    return render_template('home.html')

@app.route('/dashboard1')
def dashboard1():
    '''Returns the static dashboard'''

    return render_template('dashboard1.html')

@app.route('/dashboard2')
def dashboard2():
    '''Returns the static dashboard'''

    return render_template('dashboard2.html')

@app.route('/getembedinfo', methods=['POST'])
def getembedinfo():
    '''Returns Embed token and Embed URL'''
    idReport = request.form.get('idReport')
    print("Printing idReport: "+str(idReport))
    configresult = checkconfig()
    if configresult is None:
        try:
            accesstoken = getaccesstoken()
            print(accesstoken)
            embedinfo = getembedparam(accesstoken,idReport)
        except Exception as ex:
            return json.dumps({'errorMsg': str(ex)}), 500
    else:
        return json.dumps({'errorMsg': configresult}), 500

    return embedinfo



def checkconfig():
    '''Returns a message to user for a missing configuration'''
    if config_data['AUTHENTICATION_MODE'] == '':
        return 'Please specify one the two authentication modes'
    if config_data['AUTHENTICATION_MODE'].lower() == 'serviceprincipal' and config_data['TENANT_ID'] == '':
        return 'Tenant ID is not provided in the config.py file'
    elif config_data['REPORT_ID'] == '':
        return 'Report ID is not provided in config.py file'
    elif config_data['WORKSPACE_ID'] == '':
        return 'Workspace ID is not provided in config.py file'
    elif config_data['CLIENT_ID'] == '':
        return 'Client ID is not provided in config.py file'
    elif config_data['AUTHENTICATION_MODE'].lower() == 'masteruser':
        if config_data['POWER_BI_USER'] == '':
            return 'Master account username is not provided in config.py file'
        elif config_data['POWER_BI_PASS'] == '':
            return 'Master account password is not provided in config.py file'
    elif config_data['AUTHENTICATION_MODE'].lower() == 'serviceprincipal':
        if config_data['CLIENT_SECRET'] == '':
            return 'Client secret is not provided in config.py file'
    elif config_data['SCOPE'] == '':
        return 'Scope is not provided in the config.py file'
    elif config_data['AUTHORITY_URL'] == '':
        return 'Authority URL is not provided in the config.py file'

    return None


@app.route('/retrieve_clusters')
def retrieve_clusters():
    return str(get_clusters())
