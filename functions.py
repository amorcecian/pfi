from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import adjusted_rand_score, silhouette_score, silhouette_samples
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import sqlalchemy
from sqlalchemy  import create_engine
import pymssql

def cluster(df_stations, K):
    lat_long = df_stations[["lat", "long"]].values
    kmeans = KMeans(n_clusters=K,random_state=0).fit(lat_long)
    df = pd.DataFrame({'cluster':range(0,K), 'lat_centroide':kmeans.cluster_centers_[:,0]
        ,'long_centroide':kmeans.cluster_centers_[:,1]})

    df_mergeado = pd.merge(df_stations,pd.DataFrame(kmeans.labels_),left_index=True,right_index=True)
    df_mergeado = pd.merge(df_mergeado,df,how='left',left_on=0,right_on='cluster')
    df_mergeado = df_mergeado.drop(0,axis=1)
    df_mergeado.rename(columns={"cluster_x": "cluster", "lat_centroide_x": "lat_centroide"
        , "long_centroide_x": "long_centroide"})
    return df_mergeado


def insert_stations_with_centroids(engine,table,df):
    df.to_sql(name=table,con=engine,schema='dbo',if_exists='replace'
    ,index=False,method=None,chunksize=1000)
