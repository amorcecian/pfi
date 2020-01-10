import flask
import pymssql
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from functions import cluster, insert_stations_with_centroids
import sqlalchemy
from sqlalchemy  import create_engine

# # If want to connect with OpenShift and pass the values
# server = getenv("PYMSSQL_TEST_SERVER")
# user = getenv("PYMSSQL_TEST_USERNAME")
# password = getenv("PYMSSQL_TEST_PASSWORD")

# AzureDB
server = 'pfi-eco-bici.database.windows.net'
user = 'ciclovia@pfi-eco-bici'
password = 'Bicicleta2020'
db = 'EcoBici'
#tds_version='7.2'

# # # Local DB MAC
# server = '172.16.169.128'
# user = 'sa'
# password = 'AramLucas2019.'
# db = 'pfidb'

# # Local DB PC
# server = 'DESKTOP-3OHRULK'
# user = 'sa'
# password = 'welcome1'
# db = 'pfidb'
#######################################################
#Create connection to DB
#######################################################

#Query that retrives the usage of the stations
conn = pymssql.connect(server,user,password,db)
# conn = pymssql.connect('pfi-eco-bici.database.windows.net',
#                        user = 'ciclovia@pfi-eco-bici',
#                        password = 'Bicicleta2020',
#                        database = 'EcoBici',
#                        tds_version = '7.2')

#Connection using sqlAlchemy
conn_for_insert = fr'mssql+pymssql://'+user+':'+password+'@'+server+'/'+db
engine = create_engine(conn_for_insert)


query = open("master_query_v3.sql","r")
df_stations_usage = pd.read_sql_query(query.read(),conn)
# print(df_stations_usage.head())


stations_query = """SELECT * FROM [EcoBici].[dbo].[estaciones-de-bicicletas-publicas]"""
df_stations = pd.read_sql(stations_query,conn)
# print(df_stations.head(20))


#######################################################
# Determine % of usage of the stations
#######################################################
df_stations_usage["percentage_of_usage"] = (df_stations_usage["diferencia"]/df_stations_usage["capacidad"])*100
df_stations_usage = df_stations_usage[["nombre","nro_est","lat","long","percentage_of_usage","return_datetime"]]
df_stations_usage['return_datetime']=df_stations_usage['return_datetime'].astype('datetime64[s]')
df_stations_usage.rename(columns={'return_datetime': 'datetime'}, inplace=True)
df_stations_usage = df_stations_usage.sort_values(by=["percentage_of_usage"], ascending=True)
print(df_stations_usage.head(10))

#######################################################
# Group nearby stations
#######################################################
#-# Podría meter todo en una función y pasarle por parametro el df de stations
#-# y el K, para poder variarlo mas "facil"
df_mergeado = cluster(df_stations, 30) # Cluster into 30 groups
#print(list(df_mergeado.columns.values))
insert_stations_with_centroids(engine,'stations_with_centroids',df_mergeado)
#print(df_mergeado.head(10))

df_clusters = df_mergeado.groupby("cluster")["nro_est"].apply(list).reset_index()
df_clusters["count"] = df_clusters["nro_est"].apply(len)
#print(df_clusters.head(10))

##### Adding this
# Create a many to one with Cluster # and Station #
df_station_to_cluster = df_mergeado[['cluster','nro_est']]
# Add the cluster # to the stations usage df
df_all = pd.merge(df_stations_usage, df_station_to_cluster, on='nro_est', how='left')
# Add additional cluster data (other stations in same cluster and total stations in cluster)
df_all = pd.merge(df_all, df_clusters, on='cluster', how='left')
# Define a not very used station in a given time as having > 0 percetage of usage 
df_all['not_very_used'] = df_all['percentage_of_usage'] > 0
# Ocious clusters are the ones that at a given time have a not very used station.
df_ocious_clusters = df_all.groupby(['cluster', 'datetime'])['not_very_used'].any().reset_index()
# Get those stations and times that are very busy
df_filter = df_all[df_all['percentage_of_usage'] <= -30]
# Filter out irrelevant columns
df_filter = df_filter[['nombre', 'nro_est_x', 'percentage_of_usage', 'datetime', 'cluster', 'nro_est_y']]
# Tell if that cluster has any ociuos station at the same time
df_filter = pd.merge(df_filter, df_ocious_clusters, on=['cluster', 'datetime'], how='left')
# Filter out those that do have available bikes in stations in the same cluster
df_filter = df_filter[df_filter['not_very_used'] == False]
# df_filter now holds all stations and times that are busy with no other station with free bikes in the same cluster.
df_filter = df_filter[['nombre', 'nro_est_x', 'percentage_of_usage', 'datetime', 'cluster']]
df_stations_usage.rename(columns={'nro_est_x': 'nro_est_x'}, inplace=True)
print(len(df_filter.index))
print(df_filter.head(50))
insert_stations_with_centroids(engine,'full_stations',df_filter) #Inserting the full stations

conn.close()
#Import CSV to DB

# # Consuming USIG API to normalize the address
# p = {"calle": "OBLIGADO RAFAEL, Av.Costanera", "altura":"6182", "desambiguar":1}
# response = requests.get("https://ws.usig.buenosaires.gob.ar/rest/normalizar_y_geocodificar_direcciones",params=p)
# pepito = json.dumps(response.json())
# print(json.dumps(response.json()))
# print(pepito[2])