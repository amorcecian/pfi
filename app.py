import flask
import pymssql
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import adjusted_rand_score, silhouette_score, silhouette_samples
from sklearn.neighbors import NearestNeighbors

# # If want to connect with OpenShift and pass the values
# server = getenv("PYMSSQL_TEST_SERVER")
# user = getenv("PYMSSQL_TEST_USERNAME")
# password = getenv("PYMSSQL_TEST_PASSWORD")

# # AzureDB
# server = 'pfidbserver.database.windows.net'
# user = 'pfi_admin@pfidbserver'
# password = 'AramLucas2019.'
# db = 'pfidb'

# # # Local DB MAC
# server = '172.16.169.128'
# user = 'sa'
# password = 'AramLucas2019.'
# db = 'pfidb'

# Local DB PC
server = 'DESKTOP-3OHRULK'
user = 'sa'
password = 'welcome1'
db = 'pfidb'
#######################################################
#Create connection to DB
#######################################################

#Query that retrives the usage of the stations
conn = pymssql.connect(server,user,password,db)
query = open("master_query_v2.sql","r")
df_stations_usage = pd.read_sql_query(query.read(),conn)
# print(df_stations_usage.head())


stations_query = """SELECT * FROM [pfidb].[dbo].[estaciones-de-bicicletas-publicas]"""
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
lat_long = df_stations[["lat", "long"]].values

kmeans = KMeans(n_clusters=30,random_state=0).fit(lat_long)
df = pd.DataFrame({'cluster':range(0,30), 'lat_centroide':kmeans.cluster_centers_[:,0]
    ,'long_centroide':kmeans.cluster_centers_[:,1]})

df_mergeado = pd.merge(df_stations,pd.DataFrame(kmeans.labels_),left_index=True,right_index=True)
df_mergeado = pd.merge(df_mergeado,df,how='left',left_on=0,right_on='cluster')
df_mergeado = df_mergeado.drop(0,axis=1)
df_mergeado.rename(columns={"cluster_x": "cluster", "lat_centroide_x": "lat_centroide"
    , "long_centroide_x": "long_centroide"})

print(list(df_mergeado.columns.values))
print(df_mergeado.head(10))



############################################################
# Check if a nearby station has bikes available or not
############################################################
df_highly_used_stations = df_stations_usage[df_stations_usage['percentage_of_usage'].apply(lambda x: x <= -30)]
df_highly_used_stations['nearby_availability'] = np.nan
print(df_highly_used_stations.head())
print(df_highly_used_stations.shape[0])
# print(df_highly_used_stations['nro_est'].iloc[0])
# cluster=df_mergeado.loc[df_mergeado['nro_est'] == df_highly_used_stations['nro_est'].iloc[0]]['cluster'].item()
# print(str(cluster))

for index, row in df_highly_used_stations.iterrows():
    # Search the cluster number for that row
    cluster_aux = df_mergeado.loc[df_mergeado['nro_est'] == row['nro_est']]['cluster'].item()

    # Array of nearby stations number
    nearby_stations_numbers = df_mergeado.loc[df_mergeado['cluster'] == cluster_aux]['nro_est'].array

    # Create DF with all nearby stations at that specific time and has bike availability
    df_aux = df_stations_usage.loc[(df_stations_usage['nro_est'].isin(nearby_stations_numbers))
        & (df_stations_usage['datetime']==row['datetime'])
        & (df_stations_usage['percentage_of_usage'] > 0)]
    
    # If that DF is not empty
    if df_aux.empty:
        df_highly_used_stations.loc[index, 'nearby_availability'] = False
        # print("Empty DF")
    else:
        df_highly_used_stations.loc[index, 'nearby_availability'] = True
    
# print(df_highly_used_stations.shape)

# DF with most used stations that doesn't have a nearby station available 
df_highly_used_stations_aux = df_highly_used_stations[df_highly_used_stations['nearby_availability'] == False]
print(df_highly_used_stations_aux.groupby(['nro_est']).size().reset_index(name='counts').sort_values(by='counts', ascending=False))
# print(df_highly_used_stations_aux.shape)


# df_stations["group_diff"] = df_stations.sort_values("lat").diff().gt(max_distance).cumsum()
# print(df_stations.head())

# Joining DFs
# df_inner_out = pd.merge(df_estaciones, df_recorridos, how='inner', left_on=['nro_est'], right_on=['bici_estacion_origen'])


# print(df_inner[['nombre','nro_est','bici_estacion_origen','bici_estacion_destino','bici_tiempo_uso']].head(10))

# df = df_inner_out.groupby('nombre')['bici_Fecha_hora_retiro'].count().sort_values()
# df = df_inner_out.groupby(['bici_Fecha_hora_retiro','nombre'])['nombre'].count()#.sort_values(ascending=False)
# df = df_inner_out.groupby(['bici_Fecha_hora_retiro','nombre']).size()

# print(df.head(100))

# df = df_inner.groupby('nombre')['nombre'].count().sort_values()
# print(df)

# print(df_inner.groupby(['nombre'])['nombre'].count())

conn.close()
#Import CSV to DB

# # Consuming USIG API to normalize the address
# p = {"calle": "OBLIGADO RAFAEL, Av.Costanera", "altura":"6182", "desambiguar":1}
# response = requests.get("https://ws.usig.buenosaires.gob.ar/rest/normalizar_y_geocodificar_direcciones",params=p)
# pepito = json.dumps(response.json())
# print(json.dumps(response.json()))
# print(pepito[2])