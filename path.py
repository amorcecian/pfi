import pandas as pd
import pymssql
import collections
import logging
import sqlalchemy
from sqlalchemy  import create_engine
from functions import insert_path_areas


#######################################################
#Logger configuration
#######################################################
logstr = "%(asctime)s: %(levelname)s: Line:%(lineno)d %(message)s"
logging.basicConfig(#filename="output.log",
                    level=logging.DEBUG,
                    filemode="w",
                    format=logstr)

# AWS
server = 'pfidb.ci3ir6nuotoi.sa-east-1.rds.amazonaws.com'
user = 'admin'
password = 'AramLucas2020.'
db = 'pfidb'
#######################################################
#Create connection to DB
#######################################################

conn = pymssql.connect(server,user,password,db)

#Connection using sqlAlchemy
conn_for_insert = fr'mssql+pymssql://'+user+':'+password+'@'+server+'/'+db
engine = create_engine(conn_for_insert)
logging.info("Connection established successfully")

#######################################################
# This value defines whether two points are considered close or not.
MAXIMUM_ANGULAR_DISTANCE = 0.0025

def is_close(a, b):
    return (abs(a[0] - b[0]) < MAXIMUM_ANGULAR_DISTANCE and abs(a[1] - b[1]) < MAXIMUM_ANGULAR_DISTANCE)


c = conn.cursor()
# Bring all GPS coordinates from bike roads
c.execute("""SELECT lat_origen, long_origen FROM [dbo].[ciclovias] 
            WHERE nomoficial NOT IN ('LA PAMPA', 'TRONADOR', 'CERETTI', 'LUGONES', 
            'BONIFACIO, JOSE', 'PRIMERA JUNTA',
            'CULPINA','PEDERNERA',
            'MENDEZ DE ANDES', 'TRES ARROYOS')""")
points = c.fetchall()
c = conn.cursor()
# Bring all GPS coordinates from bike stations
c.execute("SELECT lat, long, nro_est FROM [dbo].[estaciones-de-bicicletas-publicas]")
stations = c.fetchall()
# print(stations)
conn.close()

# Start the areas array with one area having a single point
areas = [[points.pop()],]

# For each area, find points within it
for area in areas:
    # For each point in a given area, see if the unclassified points are near (belong to current area)
    for point in area:
        for item in points:
            if is_close(item, point):
                # if the point is contained in the current area, append it to it and remove from unclassified
                area.append(item)
                points.remove(item)
    if points: # If there are still points in the array, then they weren't in this area, inaugurate a new one.
        areas.append([points.pop(),])

# print(areas)
#dic = collections.defaultdict(list)
dic = {}
area_counter = 0
for area in areas:
    for point in area:
        points_dict = {'lat' : point[0], 'long' : point[1]}
        dic.update([("Area " + str(area_counter),points_dict)])
        # dic["Area " + str(area_counter)]['lat'] = point[0]
        #w.writerow(point + ("Area " + str(area_counter), ))
    area_counter +=1
# points_dict = {}
# for station in stations:
#     points_dict = {'lat' : station[0], 'long' : station[1]}
#     dic.update([('station '+str(station[2]),points_dict)])
# print(dic)

df = pd.DataFrame(dic)
df_transposed = df.transpose().reset_index()
df_transposed.columns = ['Area','lat','long']

logging.info("Inserting the final list of the areas")
insert_path_areas(engine,'path_areas',df_transposed) #Inserting the areas
logging.info("Insert of the areas finished")

# import csv
# with open('areas.csv', 'w', newline='') as f:
#     w = csv.writer(f)
#     area_counter = 0
#     for area in areas:
#         for point in area:
#             w.writerow(point + ("Area " + str(area_counter), ))
#         area_counter +=1
#     for station in stations:
#         w.writerow(station)

