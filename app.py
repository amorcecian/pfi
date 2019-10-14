import flask
import pymssql
import pandas as pd
import requests
import json
from datetime import datetime

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

#Create connection to DB
conn = pymssql.connect(server,user,password,db)
query = """SELECT * FROM [dbo].[estaciones-de-bicicletas-publicas]"""
df_estaciones = pd.read_sql(query,conn)
# print(df_estaciones.head())

query2 = """SELECT [bici_id_usuario]
	  ,DATEADD(HOUR, DATEDIFF(HOUR, 0, bici_Fecha_hora_retiro), 0) AS bici_Fecha_hora_retiro
      ,[bici_tiempo_uso]
      ,[bici_estacion_origen]
      ,[bici_estacion_destino]
      ,[bici_sexo]
      ,[bici_edad]
    FROM [pfidb].[dbo].[recorridos-realizados-2018]"""
df_recorridos = pd.read_sql(query2,conn)

# print(df_recorridos.head())

# Joining DFs
df_inner_out = pd.merge(df_estaciones, df_recorridos, how='inner', left_on=['nro_est'], right_on=['bici_estacion_origen'])


# print(df_inner[['nombre','nro_est','bici_estacion_origen','bici_estacion_destino','bici_tiempo_uso']].head(10))

# df = df_inner_out.groupby('nombre')['bici_Fecha_hora_retiro'].count().sort_values()
df = df_inner_out.groupby(['bici_Fecha_hora_retiro','nombre'])['nombre'].count()#.sort_values(ascending=False)
# df = df_inner_out.groupby(['bici_Fecha_hora_retiro','nombre']).size()

print(df.head(100))

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