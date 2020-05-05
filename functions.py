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
    #engine.execute("TRUNCATE TABLE [full_stations]")
    df.to_sql(name=table,con=engine,schema='dbo',if_exists='replace'
    ,index=False,method=None,chunksize=1000)

def generic_insert(engine,table,df):
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
    
    #Calculating the variation between one row and the next one, in percentage
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
    # and is greater than the amount of "barios" that have a valid station in it
    silhouette.sort_values('sil_coeff',ascending=False,inplace=True)
    right_K = int(silhouette.loc[silhouette['cluster']>=22]['cluster'].iloc[0])
    return right_K


def stations_usage(conn, df_stations):
    paths_2018_df = pd.read_sql_query("SELECT * FROM [dbo].[recorridos-realizados-2018]", conn)
    bak_df = paths_2018_df.copy() # I can take out this step later
    paths_2018_df = paths_2018_df.dropna()
    #######################################
    # Data Manipulation
    #######################################
    # Create the return date
    paths_2018_df['bici_tiempo_uso'] = pd.to_timedelta(paths_2018_df['bici_tiempo_uso'].astype(str))
    paths_2018_df['bici_Fecha_hora_devolucion'] = paths_2018_df['bici_Fecha_hora_retiro'] + paths_2018_df['bici_tiempo_uso']
    # Round the withdraw time
    paths_2018_df['bici_Fecha_hora_retiro_round'] = paths_2018_df['bici_Fecha_hora_retiro'].apply(lambda x: x.replace(minute=0, second=0))
    paths_2018_df['bici_Fecha_hora_devolucion_round'] = paths_2018_df['bici_Fecha_hora_devolucion'].apply(lambda x: x.replace(minute=0, second=0))
    # Compute whitdraws for each station for each hour
    withdraws_df = paths_2018_df[['bici_Fecha_hora_retiro_round', 'bici_estacion_origen', 'bici_id_usuario']].copy()
    withdraws_df = withdraws_df.groupby(['bici_Fecha_hora_retiro_round', 'bici_estacion_origen'])['bici_id_usuario'].count().reset_index().sort_values('bici_Fecha_hora_retiro_round')
    withdraws_df.rename(columns={'bici_id_usuario': 'retiros', 
                                'bici_Fecha_hora_retiro_round': 'fecha_y_hora', 
                                'bici_estacion_origen': 'estacion'}, inplace=True)
    # Compute deposits for each station for each hour
    deposits_df = paths_2018_df[['bici_Fecha_hora_devolucion_round', 'bici_estacion_destino', 'bici_id_usuario']].copy()
    deposits_df = deposits_df.groupby(['bici_Fecha_hora_devolucion_round', 'bici_estacion_destino'])['bici_id_usuario'].count().reset_index().sort_values('bici_Fecha_hora_devolucion_round')
    deposits_df.rename(columns={'bici_id_usuario': 'devoluciones', 
                                'bici_Fecha_hora_devolucion_round': 'fecha_y_hora', 
                                'bici_estacion_destino': 'estacion'}, inplace=True)
    # Merge dataframes
    stations_times_df = pd.merge(withdraws_df, deposits_df, on = ['fecha_y_hora', 'estacion'], how='outer')
    stations_times_df.fillna(0, inplace=True)
    stations_times_df['retiros'] = stations_times_df['retiros'].astype(int)
    stations_times_df['devoluciones'] = stations_times_df['devoluciones'].astype(int)
    stations_times_df['diferencia'] = stations_times_df['devoluciones'] - stations_times_df['retiros']
    stations_times_df['usos'] = stations_times_df['devoluciones'] + stations_times_df['retiros']
    #######################################
    # Adding first time of usage
    #######################################
    first_use_df = stations_times_df.sort_values(['fecha_y_hora', 'estacion'])[['fecha_y_hora', 'estacion']].drop_duplicates(subset='estacion').copy()
    tmp_df = pd.merge(first_use_df, 
                    df_stations[['nro_est', 'capacidad']], 
                    left_on='estacion', right_on='nro_est', 
                    how='left')
    stations_times_full_df = pd.merge(stations_times_df,
                                tmp_df[['fecha_y_hora', 'estacion', 'capacidad']],
                                on=['fecha_y_hora', 'estacion'],
                                how='left')
    stations_times_full_df.rename(columns={'capacidad':'bicicletas_en_estacion'}, inplace=True)
    stations_times_full_df['bicicletas_en_estacion'] += stations_times_full_df['diferencia'] 
    stations_times_full_df.sort_values('fecha_y_hora', inplace=True)

    for station in df_stations['nro_est'].unique():
        mask = stations_times_full_df['estacion'] == station
        stations_times_full_df.loc[mask, 'previous_diff'] = stations_times_full_df.loc[mask, 'diferencia'].shift(1)
        first_mask = stations_times_full_df.loc[mask, 'bicicletas_en_estacion'].isna()
        stations_times_full_df.loc[mask & first_mask, 'bicicletas_en_estacion'] = stations_times_full_df.loc[mask & first_mask, 'previous_diff']
        stations_times_full_df.loc[mask, 'bicicletas_en_estacion'] = stations_times_full_df.loc[mask, 'bicicletas_en_estacion'].cumsum()
    stations_times_full_df.drop(columns='previous_diff', inplace=True)
    stations_times_full_df.rename(columns={'estacion':'nro_est'}, inplace=True)
    return stations_times_full_df
