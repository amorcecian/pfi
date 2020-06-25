import pandas as pd
import numpy as np
import requests
import json
import random
import logging
from config import config_data
from datetime import datetime
from data_bike.functions import *
import sqlalchemy
from sqlalchemy  import create_engine
from geopy import Point
from geopy.distance import distance

# DB Credentials
server = config_data['SERVER']
user = config_data['USER']
password = config_data['PASSWORD']
db = config_data['DB']

# server = app.config_data['SERVER']
# user = app.config_data['USER']
# password = app.config_data['PASSWORD']
# db = app.config_data['DB']  


#######################################################
#Logger configuration
#######################################################
logstr = "%(asctime)s: %(levelname)s: Line:%(lineno)d %(message)s"
logging.basicConfig(#filename="output.log",
                    level=logging.INFO,
                    filemode="w",
                    format=logstr)

#######################################################
#Create connection to DB
#######################################################

#conn = pymssql.connect(server,user,password,db)

#Connection using sqlAlchemy
def engine_creation():
    logging.info(f"Connecting to {server} database")
    conn_for_insert = fr'mssql+pymssql://'+user+':'+password+'@'+server+'/'+db
    engine = create_engine(conn_for_insert)
    logging.info("Connection established successfully")
    return engine

#######################################################
#######################################################
######### FUNCTIONS DEFINITION BEGIN ##################
#######################################################
#######################################################

#######################################################
# Group nearby stations
#######################################################
def group_stations(engine):
    logging.info("Cleaning the database")
    engine.execute("TRUNCATE TABLE [dbo].[stations_with_centroids]")
    engine.execute("TRUNCATE TABLE [dbo].[stations_clusters_usage]")
    engine.execute("TRUNCATE TABLE [dbo].[average_fuller_clusters]")
    engine.execute("DELETE FROM [dbo].[estaciones-de-bicicletas-publicas] WHERE nro_est > 200")
    logging.info("Tables erased")

    stations_query = """SELECT * FROM [estaciones-de-bicicletas-publicas]"""
    df_stations = pd.read_sql(stations_query,engine)
    logging.info("Stations loaded")

    logging.info("Calculating the right K")

    # Commenting this because adding a stations to a cluster to test its variation
    K = defining_right_k(df_stations)
    #engine.execute('INSERT INTO k_value VALUES ({})'.format(K))

    # K = engine.execute('SELECT TOP 1 value FROM k_value').fetchone()[0]

    logging.info(f"The right K is {str(K)}")
    logging.info("Starting to group nearby stations")
    df_merged = cluster(df_stations, K) # Cluster into K groups

    df_merged_radius = determing_cluster_radius(df_merged) # Adding cluster's radius to the df
    insert_stations_with_centroids(engine,'stations_with_centroids',df_merged_radius)
    logging.info("Stations with centroids information loaded to the DB")

    df_clusters = df_merged.groupby("cluster")["nro_est"].apply(list).reset_index()
    df_clusters["count"] = df_clusters["nro_est"].apply(len)
    return None


def jsonify_usig(res):
    return json.loads(res.text[1:-1])

def correcting_lat_lon(x,y):
    # Turning original lat long to corrected lat long
    URL="https://ws.usig.buenosaires.gob.ar/rest/convertir_coordenadas"
    # X is longitude and Y is latitude
    params = {'x':x, 'y':y,'output':'lonlat'}
    corrected_lonlat = requests.get(URL,params=params).json()
    corrected_lonlat = corrected_lonlat['resultado']
    return (float(corrected_lonlat['y']),float(corrected_lonlat['x']))

def new_lat_long(lat1, lon1):
    # given: lat1, lon1, b = bearing in degrees, d = distance in kilometers
    b = random.randint(1, 360)
    logging.info(f"Bearing is equal to: {str(b)}")
    d = 0.2
    origin = Point(lat1, lon1)
    destination = distance(kilometers=d).destination(origin, b)
    return destination

def new_station_number():
    engine = engine_creation()
    return engine.execute("SELECT MAX(nro_est)+1 FROM [estaciones-de-bicicletas-publicas]").fetchone()[0]

def add_station(nombre, capacidad, cluster,engine):
    # ONLY NEEDS NAME, CAPACITY AND CLUSTER!!
    logging.info("Adding new station to cluster {}".format(str(cluster)))
    new_station = {
        'long':0,
        'lat':0,
        'nombre':nombre,
        'domicilio':'',
        'nro_est':0,
        'dire_norm':'',
        'capacidad':int(capacidad),
        'cluster':int(cluster),
        'lat_centroide':0,
        'long_centroide':0,
        'radius':0
    }

    new_station['nro_est'] = engine.execute("SELECT MAX(nro_est)+1 FROM [estaciones-de-bicicletas-publicas]").fetchone()[0]

    cluster_info_query = """SELECT TOP 1 lat, long, lat_centroide, long_centroide, radius
                            FROM [pfidb].[dbo].[stations_clusters_usage]
                            WHERE cluster={}
                            ORDER BY bicicletas_en_estacion ASC""".format(new_station['cluster'])

    cluster_station_info = engine.execute(cluster_info_query).fetchone()
    centroid_location = (cluster_station_info[2],cluster_station_info[3])
    new_station['lat_centroide'] = cluster_station_info[2]
    new_station['long_centroide'] = cluster_station_info[3]
    new_station['radius'] = cluster_station_info[4]

    # Calculating new lat lon
    destination = new_lat_long(cluster_station_info[0], cluster_station_info[1])
    lat2, lon2 = destination.latitude, destination.longitude
    new_station_location = (lat2, lon2)

    while distance(new_station_location, centroid_location).km >= cluster_station_info[4]:
        destination = new_lat_long(cluster_station_info[0], cluster_station_info[1])
        lat2, lon2 = destination.latitude, destination.longitude
        new_station_location = (lat2, lon2)

    # Turning lat long to address
    URL="https://ws.usig.buenosaires.gob.ar/geocoder/2.2/reversegeocoding"
    # X is longitude and Y is latitude
    params = {'x':lon2, 'y':lat2}
    usig_address = jsonify_usig(requests.get(URL,params=params))

    new_station['domicilio'] = usig_address['puerta']
    new_station['dire_norm'] = usig_address['puerta']

    corrected_lonlat = correcting_lat_lon(usig_address['puerta_x'],usig_address['puerta_y'])
    new_station['lat'] = corrected_lonlat[0]
    new_station['long'] = corrected_lonlat[1]

    logging.info("New station created with number: "+ str(new_station['nro_est']))

    logging.info("Adding new station to [stations_with_centroids]")
    stations_clusters_query = """SELECT * FROM [stations_with_centroids]"""
    df_merged = pd.read_sql(stations_clusters_query,engine)
    df_merged = df_merged.append(new_station, ignore_index=True)
    insert_stations_with_centroids(engine,'stations_with_centroids',df_merged)

    logging.info("Adding new station to [estaciones-de-bicicletas-publicas]")
    aux_keys = ['long','lat','nombre','domicilio','nro_est','dire_norm','capacidad']
    new_station_aux = { key: new_station[key] for key in aux_keys }
    stations_query = """SELECT * FROM [estaciones-de-bicicletas-publicas]"""
    df_stations_aux = pd.read_sql(stations_query,engine)
    df_stations_aux = df_stations_aux.append(new_station_aux, ignore_index=True)
    generic_insert(engine,'estaciones-de-bicicletas-publicas',df_stations_aux)
    
    # df_merged_radius = pd.read_sql(stations_clusters_query,engine)

    # df_stations = pd.read_sql(stations_query,engine)
    # logging.info("Stations loaded")

    # Cleaning tables
    engine.execute("TRUNCATE TABLE [dbo].[stations_clusters_usage]")
    engine.execute("TRUNCATE TABLE [dbo].[average_fuller_clusters]")
    logging.info("Tables erased")

    return None
    # return str(new_station['nro_est'])


def calculate_stations_usage(engine):
    # Retrieving the stations
    stations_query = """SELECT * FROM [estaciones-de-bicicletas-publicas]"""
    df_stations = pd.read_sql(stations_query,engine)
    # Retrieving the clusters and stations
    stations_clusters_query = """SELECT * FROM [stations_with_centroids]"""
    df_merged_radius = pd.read_sql(stations_clusters_query,engine)

    logging.info("Calculating the stations usage")
    df_stations_usage = stations_usage(engine,df_stations)
    stations_avg_df = df_stations_usage.groupby('nro_est')['bicicletas_en_estacion','usos'].mean()
    stations_avg_df = stations_avg_df.sort_values('bicicletas_en_estacion').reset_index()

    # DataFrame adding the month and year to the stations usage average DataFrame
    # Not used for now
    # stations_avg_month_df = df_stations_usage.copy()
    # stations_avg_month_df['year_month'] = stations_avg_month_df['fecha_y_hora'].apply(lambda x: x.strftime('%Y-%m'))
    # stations_avg_month_df = stations_avg_month_df.groupby(['nro_est','year_month'])['bicicletas_en_estacion','usos'].mean()
    # stations_avg_month_df = stations_avg_month_df.sort_values('bicicletas_en_estacion').reset_index()
    # logging.info("Stations usage average df created")

    #####################################################################################
    #####################################################################################
    stations_clusters_original = pd.merge(df_merged_radius,stations_avg_df, on='nro_est', how='left')
    stations_clusters_original['usos'].fillna(0, inplace=True)
    stations_clusters_original['bicicletas_en_estacion'].fillna(stations_clusters_original['capacidad'], inplace=True)
    stations_clusters_usage = stations_clusters_original.copy()
    stations_clusters_usage['very_used'] = np.where(stations_clusters_usage['bicicletas_en_estacion'] < 0, True, False)

    logging.info("Inserting the Stations with their clusters and usage")
    generic_insert(engine,'stations_clusters_usage',stations_clusters_usage) #Inserting the stations
    logging.info("Insert of the stations finished")

    average_fuller_clusters = stations_clusters_original[['cluster','lat_centroide','long_centroide','radius','bicicletas_en_estacion','usos']].copy()
    average_fuller_clusters = average_fuller_clusters.groupby(['cluster','lat_centroide','long_centroide','radius'])['bicicletas_en_estacion','usos'].mean().reset_index()
    average_fuller_clusters['very_used'] = np.where(average_fuller_clusters['bicicletas_en_estacion'] < 0, True, False)

    logging.info("Inserting Clusters and their ussage")
    generic_insert(engine,'average_fuller_clusters',average_fuller_clusters) #Inserting the clusters
    logging.info("Insert of the clusters finished")


def get_stations():
    engine = engine_creation()
    stations_query = """SELECT * FROM [estaciones-de-bicicletas-publicas]"""
    df_stations = pd.read_sql(stations_query,engine)
    logging.info("Stations loaded")
    return df_stations.to_json(orient='records')
#######################################################
#######################################################
########## FUNCTIONS DEFINITION END ###################
#######################################################
#######################################################


#######################################################
# Determine the usage of the stations
#######################################################
# stations_query = """SELECT * FROM [estaciones-de-bicicletas-publicas]"""
# df_stations = pd.read_sql(stations_query,engine)
# logging.info("Query read successfully")

# engine = engine_creation()
# df_merged_radius,df_stations = group_stations(engine)
# calculate_stations_usage(df_merged_radius,df_stations,engine)

# df_merged_radius,df_stations = add_station('Test Retiro I',20,18)
# df_merged_radius,df_stations = add_station('Test Retiro II',200,18)
#df_merged_radius,df_stations = add_station('Test Retiro III',1000,18)



#conn.close()
#Import CSV to DB

# # Consuming USIG API to normalize the address
# p = {"calle": "OBLIGADO RAFAEL, Av.Costanera", "altura":"6182", "desambiguar":1}
# response = requests.get("https://ws.usig.buenosaires.gob.ar/rest/normalizar_y_geocodificar_direcciones",params=p)
# pepito = json.dumps(response.json())
# print(json.dumps(response.json()))
# print(pepito[2])
