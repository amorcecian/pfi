import flask
import pymssql
import pandas as pd
import numpy as np
import requests
import json
import random
import logging
from datetime import datetime
from functions import *
import sqlalchemy
from sqlalchemy  import create_engine

# # If want to connect with OpenShift and pass the values
# server = getenv("PYMSSQL_TEST_SERVER")
# user = getenv("PYMSSQL_TEST_USERNAME")
# password = getenv("PYMSSQL_TEST_PASSWORD")

# AzureDB
# server = 'pfi-eco-bici.database.windows.net'
# user = 'ciclovia@pfi-eco-bici'
# password = 'Bicicleta2020'
# db = 'EcoBici'

# # AWS
# server = 'pfidb.ci3ir6nuotoi.sa-east-1.rds.amazonaws.com'
# user = 'admin'
# password = 'AramLucas2020.'
# db = 'pfidb'

# Local DB PC
server = 'DESKTOP-3OHRULK'
user = 'sa'
password = 'welcome1'
db = 'pfidb'

#######################################################
#Logger configuration
#######################################################
logstr = "%(asctime)s: %(levelname)s: Line:%(lineno)d %(message)s"
logging.basicConfig(#filename="output.log",
                    level=logging.DEBUG,
                    filemode="w",
                    format=logstr)

#######################################################
#Create connection to DB
#######################################################

conn = pymssql.connect(server,user,password,db)

#Connection using sqlAlchemy
conn_for_insert = fr'mssql+pymssql://'+user+':'+password+'@'+server+'/'+db
engine = create_engine(conn_for_insert)
logging.info("Connection established successfully")
'''
###################################################################
###################################################################
###################################################################
###################################################################
# ONLY DOING THIS FOR TESTING, THEN I'LL PUT THIS IN ANOTHER FUNCTION
# Loading the stations with cluster from the table
def jsonify_usig(res):
    return json.loads(res.text[1:-1])


# ONLY NEEDS NAME, CAPACITY AND CLUSTER!!
new_station = {
    'long':0,
    'lat':0,
    'nombre':'Test 5 para variar cluster 15',
    'domicilio':'',
    'nro_est':0,
    'dire_norm':'',
    'capacidad':100,
    'cluster':15,
    'lat_centroide':0,
    'long_centroide':0
}

new_station['nro_est'] = engine.execute("SELECT MAX(nro_est)+1 FROM [estaciones-de-bicicletas-publicas]").fetchone()[0]

cluster_info_query = """SELECT lat_centroide, long_centroide 
                FROM [pfidb].[dbo].[stations_clusters_usage]
                WHERE cluster={}
                GROUP BY lat_centroide,long_centroide""".format(new_station['cluster'])

cluster_lat_long = engine.execute(cluster_info_query).fetchone()
#new_station['lat'] = cluster_lat_long[0]
#new_station['long'] = cluster_lat_long[1]
new_station['lat_centroide'] = cluster_lat_long[0]
new_station['long_centroide'] = cluster_lat_long[1]

lat_long_lists_query = """SELECT lat, long 
                FROM [pfidb].[dbo].[stations_clusters_usage]
                WHERE cluster={}""".format(new_station['cluster'])

lat_list = []
long_list = []
for i in engine.execute(lat_long_lists_query).fetchall():
    lat_list.append(i[0])
    long_list.append(i[1])

lat_aux = (random.choice(lat_list)+random.choice(lat_list))/2
while lat_aux in lat_list:
    lat_aux = (random.choice(lat_list)+random.choice(lat_list))/2


long_aux = (random.choice(long_list)+random.choice(long_list))/2
while long_aux in long_list:
    long_aux = (random.choice(long_list)+random.choice(long_list))/2

new_station['lat'] = lat_aux
new_station['long'] = long_aux

# Turning lat long to address
URL="https://ws.usig.buenosaires.gob.ar/geocoder/2.2/reversegeocoding"
# X is longitude and Y is latitude
params = {'x':new_station['long'], 'y':new_station['lat']}
usig_address = jsonify_usig(requests.get(URL,params=params))

new_station['domicilio'] = usig_address['puerta']
new_station['dire_norm'] = usig_address['puerta']


stations_clusters_query = """SELECT * FROM [stations_with_centroids]"""
df_merged = pd.read_sql(stations_clusters_query,conn)
df_merged = df_merged.append(new_station, ignore_index=True)
insert_stations_with_centroids(engine,'stations_with_centroids',df_merged)


aux_keys = ['long','lat','nombre','domicilio','nro_est','dire_norm','capacidad']
new_station_aux = { key: new_station[key] for key in aux_keys }
stations_query = """SELECT * FROM [estaciones-de-bicicletas-publicas]"""
df_stations = pd.read_sql(stations_query,conn)
df_stations = df_stations.append(new_station_aux, ignore_index=True)
generic_insert(engine,'estaciones-de-bicicletas-publicas',df_stations)

df_merged = pd.read_sql(stations_clusters_query,conn)

'''
###################################################################
###################################################################
###################################################################
###################################################################


stations_query = """SELECT * FROM [estaciones-de-bicicletas-publicas]"""
df_stations = pd.read_sql(stations_query,conn)
logging.info("Query read successfully")

#Query that retrives the usage of the stations
# query = open("master_query_v3.sql","r")
# df_stations_usage = pd.read_sql_query(query.read(),conn)
logging.info("Calculating the stations usage")
df_stations_usage = stations_usage(conn,df_stations)
stations_avg_df = df_stations_usage.groupby('nro_est')['bicicletas_en_estacion','usos'].mean()
stations_avg_df = stations_avg_df.sort_values('bicicletas_en_estacion').reset_index()

# DataFrame adding the month and year to the stations usage average DataFrame
# Not used for now
stations_avg_month_df = df_stations_usage.copy()
stations_avg_month_df['year_month'] = stations_avg_month_df['fecha_y_hora'].apply(lambda x: x.strftime('%Y-%m'))
stations_avg_month_df = stations_avg_month_df.groupby(['nro_est','year_month'])['bicicletas_en_estacion','usos'].mean()
stations_avg_month_df = stations_avg_month_df.sort_values('bicicletas_en_estacion').reset_index()
logging.info("Stations usage average df created")

#######################################################
# Determine % of usage of the stations
#######################################################
# df_stations_usage["percentage_of_usage"] = (df_stations_usage["diferencia"]/df_stations_usage["capacidad"])*100
# df_stations_usage = df_stations_usage[["nombre","nro_est","lat","long","percentage_of_usage","return_datetime"]]
# df_stations_usage['return_datetime']=df_stations_usage['return_datetime'].astype('datetime64[s]')
# df_stations_usage.rename(columns={'return_datetime': 'datetime'}, inplace=True)
# df_stations_usage = df_stations_usage.sort_values(by=["percentage_of_usage"], ascending=True)
# #print(df_stations_usage.head(10))
# logging.info("Percentage of usage of the stations determined")

#######################################################
# Group nearby stations
#######################################################

logging.info("Calculating the right K")

# Commenting this because adding a stations to a cluster to test its variation
K = defining_right_k(df_stations)
#engine.execute('INSERT INTO k_value VALUES ({})'.format(K))

# K = engine.execute('SELECT TOP 1 value FROM k_value').fetchone()[0]

logging.info("The right K is {}".format(str(K)))
logging.info("Starting to group nearby stations")
df_merged = cluster(df_stations, K) # Cluster into K groups
insert_stations_with_centroids(engine,'stations_with_centroids',df_merged)
logging.info("Stations with centroids information loaded to the DB")

df_clusters = df_merged.groupby("cluster")["nro_est"].apply(list).reset_index()
df_clusters["count"] = df_clusters["nro_est"].apply(len)


##### Adding this
# # Create a many to one with Cluster # and Station #
# df_station_to_cluster = df_merged[['cluster','nro_est']]
# # Add the cluster # to the stations usage df
# df_all = pd.merge(df_stations_usage, df_station_to_cluster, on='nro_est', how='left')
# # Add additional cluster data (other stations in same cluster and total stations in cluster)
# df_all = pd.merge(df_all, df_clusters, on='cluster', how='left')
# # Define a not very used station in a given time as having > 0 percetage of usage 
# df_all['not_very_used'] = df_all['percentage_of_usage'] > 0
# # Ocious clusters are the ones that at a given time have a not very used station.
# df_ocious_clusters = df_all.groupby(['cluster', 'datetime'])['not_very_used'].any().reset_index()
# # Get those stations and times that are very busy
# df_filter = df_all[df_all['percentage_of_usage'] <= -30]
# # Filter out irrelevant columns
# df_filter = df_filter[['nombre', 'nro_est_x', 'percentage_of_usage', 'datetime', 'cluster', 'nro_est_y']]
# # Tell if that cluster has any ociuos station at the same time
# df_filter = pd.merge(df_filter, df_ocious_clusters, on=['cluster', 'datetime'], how='left')
# # Filter out those that do have available bikes in stations in the same cluster
# df_filter = df_filter[df_filter['not_very_used'] == False]
# # df_filter now holds all stations and times that are busy with no other station with free bikes in the same cluster.
# df_filter = df_filter[['nombre', 'nro_est_x', 'percentage_of_usage', 'datetime', 'cluster']]
# df_stations_usage.rename(columns={'nro_est_x': 'nro_est_x'}, inplace=True)
# logging.info("Nearby stations grouping finished")

# print(len(df_filter.index))
# print(df_filter.head(50))
# logging.info("Inserting the final list of the stations that are full")
# insert_stations_with_centroids(engine,'full_stations',df_filter) #Inserting the full stations
# logging.info("Insert of the stations that are full finished")

#####################################################################################
#####################################################################################
stations_clusters_original = pd.merge(df_merged,stations_avg_df, on='nro_est', how='left')
stations_clusters_original['usos'].fillna(0, inplace=True)
stations_clusters_original['bicicletas_en_estacion'].fillna(stations_clusters_original['capacidad'], inplace=True)
stations_clusters_usage = stations_clusters_original.copy()
stations_clusters_usage['very_used'] = np.where(stations_clusters_usage['bicicletas_en_estacion'] < 0, True, False)

logging.info("Inserting the Stations with their clusters and usage")
generic_insert(engine,'stations_clusters_usage',stations_clusters_usage) #Inserting the stations
logging.info("Insert of the stations finished")

average_fuller_clusters = stations_clusters_original[['cluster','lat_centroide','long_centroide','bicicletas_en_estacion','usos']].copy()
average_fuller_clusters = average_fuller_clusters.groupby(['cluster','lat_centroide','long_centroide'])['bicicletas_en_estacion','usos'].mean().reset_index()
average_fuller_clusters['very_used'] = np.where(average_fuller_clusters['bicicletas_en_estacion'] < 0, True, False)

logging.info("Inserting Clusters and their ussage")
generic_insert(engine,'average_fuller_clusters',average_fuller_clusters) #Inserting the clusters
logging.info("Insert of the clusters finished")

conn.close()
#Import CSV to DB

# # Consuming USIG API to normalize the address
# p = {"calle": "OBLIGADO RAFAEL, Av.Costanera", "altura":"6182", "desambiguar":1}
# response = requests.get("https://ws.usig.buenosaires.gob.ar/rest/normalizar_y_geocodificar_direcciones",params=p)
# pepito = json.dumps(response.json())
# print(json.dumps(response.json()))
# print(pepito[2])
