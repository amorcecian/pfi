import pandas as pd

# Loading CSV to DataFrame
df_recorridos = pd.read_csv("recorridos-realizados-2018.csv")

#Replacing string value in date field
df_recorridos["bici_tiempo_uso"]=df_recorridos["bici_tiempo_uso"].str.replace('0 days','',regex=False)
df_recorridos["bici_tiempo_uso"]=df_recorridos["bici_tiempo_uso"].str[:9]

df_recorridos.head() # Testing df

# New DataFrame with some columns less than the first one
df_recorridos_simplificado = df_recorridos[["bici_id_usuario","bici_Fecha_hora_retiro","bici_tiempo_uso","bici_estacion_origen","bici_estacion_destino","bici_sexo","bici_edad"]]

df_recorridos_simplificado.head() # Testing new df

# Saving new DF to CSV
df_recorridos_simplificado.to_csv(r'recorridos-realizados-2018-corregido.csv')