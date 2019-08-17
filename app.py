import flask
import pymssql
import pandas as pd

# If want to connect with OpenShift and pass the values
# server = getenv("PYMSSQL_TEST_SERVER")
# user = getenv("PYMSSQL_TEST_USERNAME")
# password = getenv("PYMSSQL_TEST_PASSWORD")

server = 'pfidbserver.database.windows.net'
user = 'pfi_admin@pfidbserver'
password = 'AramLucas2019.'
db = 'pfidb'

#Create connection to DB
conn = pymssql.connect(server,user,password,db)
c = conn.cursor()
c.execute("""SELECT * FROM [dbo].[estaciones-de-bicicletas-publicas]""")
for row in c.fetchall():
    print('id: '+ str(row[0])+'   Nombre: '+str(row[1]))

#Read CSV to df
df = pd.read_csv("recorridos-realizados-2018.csv")
print(df.head())


conn.close()
#Import CSV to DB