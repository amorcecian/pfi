import flask
import pymssql

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
c.execute("""SELECT * FROM dbo.prueba_aram""")
for row in c.fetchall():
    print('id: '+ str(row[0])+'   Nombre: '+str(row[1]))

#Read CSV to df


conn.close()
#Import CSV to DB