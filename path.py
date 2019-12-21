import pandas as pd
import pymssql

# This value defines whether two points are considered close or not.
MAXIMUM_ANGULAR_DISTANCE = 0.0025

def is_close(a, b):
    return (abs(a[0] - b[0]) < MAXIMUM_ANGULAR_DISTANCE and abs(a[1] - b[1]) < MAXIMUM_ANGULAR_DISTANCE)

# Local DB PC
server = 'DESKTOP-3OHRULK'
user = 'sa'
password = 'welcome1'
db = 'pfidb'
#######################################################
#Create connection to DB
#######################################################

conn = pymssql.connect(server,user,password,db)


c = conn.cursor()
# Bring all GPS coordinates from bike roads
c.execute("SELECT lat_origen, long_origen FROM [dbo].[ciclovias]")
points = c.fetchall()
c = conn.cursor()
# Bring all GPS coordinates from bike stations
c.execute("SELECT lat, long, 'station' FROM [dbo].[estaciones-de-bicicletas-publicas]")
stations = c.fetchall()
print(stations)
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


import csv
with open('areas.csv', 'w', newline='') as f:
    w = csv.writer(f)
    area_counter = 0
    for area in areas:
        for point in area:
            w.writerow(point + ("Area " + str(area_counter), ))
        area_counter +=1
    for station in stations:
        w.writerow(station)

