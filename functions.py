from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import adjusted_rand_score, silhouette_score, silhouette_samples
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import sqlalchemy
from sqlalchemy  import create_engine
import pymssql

# This function needs two parameters:
#   - Dataframe with lat and long fields. Lat represents the latitude of the 
#     station and long the longitude of it
#   - K: Number of centroids to use by the K-Means algorithm. This is going to
#     be fixed because we've tested some Ks and found the best for this exercise
def cluster(df_stations, K):
    # We are going to create lat_long dataframe, which is a subset of 
    # df_stations. We're going to cluster that dataframe in centroids in order
    # to determine which stations are close to each other.
    lat_long = df_stations[["lat", "long"]].values
    # Now we apply the KMeans algorithm specifying the number of clusters and
    # the random state to make the result reproducible (the result is going to
    # be always the same if the dataset doesn't change)
    kmeans = KMeans(n_clusters=K,random_state=0).fit(lat_long)
    # Generate a dataframe with the result of the KMeans algorithm. This df is 
    # goint to have 3 columns. The cluster number, the latitude and the longitude 
    # of it
    df = pd.DataFrame({'cluster':range(0,K), 'lat_centroide':kmeans.cluster_centers_[:,0]
        ,'long_centroide':kmeans.cluster_centers_[:,1]})

    # Now we're going to merge the stations dataframe with the new one ir oder 
    # to add the centroids information to each row of the stations dataframe
    df_mergeado = pd.merge(df_stations,pd.DataFrame(kmeans.labels_),left_index=True,right_index=True)
    df_mergeado = pd.merge(df_mergeado,df,how='left',left_on=0,right_on='cluster')
    df_mergeado = df_mergeado.drop(0,axis=1)
    df_mergeado.rename(columns={"cluster_x": "cluster", "lat_centroide_x": "lat_centroide"
        , "long_centroide_x": "long_centroide"})
    return df_mergeado


def insert_stations_with_centroids(engine,table,df):
    engine.execute("TRUNCATE TABLE [full_stations]")
    df.to_sql(name=table,con=engine,schema='dbo',if_exists='append'
    ,index=False,method=None,chunksize=1000)

def insert_path_areas(engine,table,df):
    df.to_sql(name=table,con=engine,schema='dbo',if_exists='replace'
    ,index=False,method=None,chunksize=1000)
