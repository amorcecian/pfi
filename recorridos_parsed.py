import pandas as pd

# Loading CSV to DataFrame
df_recorridos = pd.read_csv("recorridos-realizados-2019.csv")

#Replacing string value in date field
df_recorridos["bici_tiempo_uso"]=df_recorridos["duracion_recorrido"].str.replace('0 days','',regex=False)
df_recorridos["bici_tiempo_uso"]=df_recorridos["bici_tiempo_uso"].str[:9]

#df_recorridos.head() # Testing df

# New DataFrame with some columns less than the first one
df_recorridos_simplificado = df_recorridos[["id_usuario","fecha_origen_recorrido","fecha_destino_recorrido","id_estacion_origen","id_estacion_destino","genero_usuario","edad_usuario"]]

#df_recorridos_simplificado.head() # Testing new df

# Saving new DF to CSV
df_recorridos_simplificado.to_csv(r'recorridos-realizados-2019-corregido.csv',index=False)