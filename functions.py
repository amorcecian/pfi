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
    df_merged = pd.merge(df_stations,pd.DataFrame(kmeans.labels_),left_index=True,right_index=True)
    df_merged = pd.merge(df_merged,df,how='left',left_on=0,right_on='cluster')
    df_merged = df_merged.drop(0,axis=1)
    df_merged.rename(columns={"cluster_x": "cluster", "lat_centroide_x": "lat_centroide"
        , "long_centroide_x": "long_centroide"})
    return df_merged


def insert_stations_with_centroids(engine,table,df):
    engine.execute("TRUNCATE TABLE [full_stations]")
    df.to_sql(name=table,con=engine,schema='dbo',if_exists='replace'
    ,index=False,method=None,chunksize=1000)

def insert_path_areas(engine,table,df):
    df.to_sql(name=table,con=engine,schema='dbo',if_exists='replace'
    ,index=False,method=None,chunksize=1000)


def defining_right_k(df_stations):
    #Calculating the sse for all the Ks
    lat_long = df_stations[["lat", "long"]].values
    sse_df = pd.DataFrame(columns=['K','sse']) #Creating new DF to store K and sse
    for k in range(1, int(len(df_stations))):
        #Calculating KMeans w/ each K to store their sse
        kmeans = KMeans(n_clusters=k,random_state=0,max_iter=1000).fit(lat_long)
        #Saving the sse for that k
        sse_df = sse_df.append({'K':k, 'sse':kmeans.inertia_},ignore_index=True)
    
    #Calculating the variation betwenn one row and the next one, in percentage
    sse_df['variation'] = (sse_df['sse'].pct_change())*-1
    #Searching for a variation drop bigger that 10%
    i = sse_df.loc[(sse_df['variation'] <= 0.1)].index[0]
    lower_limit = int(sse_df.iloc[i]['K']) #Determing the lower limit
    #Determing the upper limit that is going to be the 10% of the total
    #amout of the stations
    upper_limit = int(lower_limit  + round((len(df_stations)*0.1)))
    
    #Creating new DF to the cluster number and the silhouette coefficient
    silhouette = pd.DataFrame(columns=['cluster','sil_coeff']) 
    for n_cluster in range(lower_limit, upper_limit):
        #Calculating KMeans w/ each cluster number to store their silhouette coefficient
        kmeans = KMeans(n_clusters=n_cluster,random_state=0).fit(lat_long)
        label = kmeans.labels_
        sil_coeff = silhouette_score(lat_long, label, metric='euclidean')
        silhouette = silhouette.append({'cluster':n_cluster, 'sil_coeff':sil_coeff},ignore_index=True)
    #Selecting the cluster number that has the hihhest silhouette coefficient
    #to be the right K
    right_K = int(silhouette.loc[silhouette['sil_coeff'].idxmax()]['cluster'])
    return right_K