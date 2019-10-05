import flask
import pymssql
import pandas as pd
import requests
import json

# If want to connect with OpenShift and pass the values
# server = getenv("PYMSSQL_TEST_SERVER")
# user = getenv("PYMSSQL_TEST_USERNAME")
# password = getenv("PYMSSQL_TEST_PASSWORD")

# AzureDB
# server = 'pfidbserver.database.windows.net'
# user = 'pfi_admin@pfidbserver'
# password = 'AramLucas2019.'
# db = 'pfidb'

# Local DB
server = '172.16.169.128'
user = 'sa'
password = 'AramLucas2019.'
db = 'pfidb'

#Create connection to DB
conn = pymssql.connect(server,user,password,db)
query = """SELECT * FROM [dbo].[estaciones-de-bicicletas-publicas]"""
df_estaciones = pd.read_sql(query,conn)
#print(df_estaciones.head())

#Read CSV to df
df_recorridos = pd.read_csv("recorridos-realizados-2018.csv")
#print(df.head())

# Joining DFs
df_inner = pd.merge(df_estaciones, df_recorridos, how='inner', left_on=['nro_est'], right_on=['bici_estacion_origen'])

# print(df_inner[['nombre','nro_est','bici_estacion_origen','bici_estacion_destino','bici_tiempo_uso']].head(10))

df = df_inner.groupby('nombre')['nombre'].count().sort_values()
# print(df)

# print(df_inner.groupby(['nombre'])['nombre'].count())

conn.close()
#Import CSV to DB

# Consuming USIG API to normalize the address
p = {"calle": "OBLIGADO RAFAEL, Av.Costanera", "altura":"6182", "desambiguar":1}
response = requests.get("https://ws.usig.buenosaires.gob.ar/rest/normalizar_y_geocodificar_direcciones",params=p)
pepito = json.dumps(response.json())
print(json.dumps(response.json()))
print(pepito[2])