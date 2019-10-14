/****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP (1000) [bici_id_usuario]
      ,[bici_Fecha_hora_retiro]
      ,[bici_tiempo_uso]
      ,[bici_estacion_origen]
      ,[bici_estacion_destino]
      ,[bici_sexo]
      ,[bici_edad]
  FROM [pfidb].[dbo].[recorridos-realizados-2018]
  where [bici_tiempo_uso] IS NULL

SELECT TOP 10 * FROM [pfidb].[dbo].[recorridos-realizados-2018]

SELECT bici_estacion_destino, return_datetime, min_of_usage ,COUNT(bici_estacion_destino) count_destino 
FROM (
	SELECT bici_estacion_destino
	,DATEPART(mi,bici_tiempo_uso) AS min_of_usage
	,CASE
		WHEN DATEPART(mi,bici_tiempo_uso) < 10 THEN (DATEADD(HOUR, DATEDIFF(HOUR, 0, CAST(CONVERT(date,bici_Fecha_hora_retiro) AS datetime) + CAST(DATEADD(MI, DATEDIFF(MI, 8, bici_Fecha_hora_retiro), bici_tiempo_uso) AS datetime) ), 0))
		WHEN DATEPART(mi,bici_tiempo_uso) > 10 THEN DATEADD(HOUR, 1, (DATEADD(HOUR, DATEDIFF(HOUR, 0, CAST(CONVERT(date,bici_Fecha_hora_retiro) AS datetime) + CAST(DATEADD(MI, DATEDIFF(MI, 8, bici_Fecha_hora_retiro), bici_tiempo_uso) AS datetime) ), 0)))
		ELSE [bici_Fecha_hora_retiro]
	END AS return_datetime
	FROM [pfidb].[dbo].[recorridos-realizados-2018]
	WHERE [bici_tiempo_uso] IS NOT NULL) as aux_table
GROUP BY bici_estacion_destino, return_datetime,min_of_usage
ORDER BY count_destino DESC


-- SELECT DATEADD(day, DATEDIFF(day, 0, bici_Fecha_hora_retiro), bici_tiempo_uso)
 SELECT TOP 10 bici_Fecha_hora_retiro FROM [pfidb].[dbo].[recorridos-realizados-2018]


SELECT DATEADD(HOUR, DATEDIFF(HOUR, 0, rr.bici_Fecha_hora_retiro), 0) AS bici_Fecha_hora_retiro_aux, origen.nombre, 
rr.bici_estacion_origen ,COUNT(origen.nombre) AS count_origen, COUNT(destino.nombre) AS count_destino
FROM [pfidb].[dbo].[recorridos-realizados-2018] rr
LEFT JOIN [pfidb].[dbo].[estaciones-de-bicicletas-publicas] origen on rr.bici_estacion_origen=origen.nro_est
LEFT JOIN [pfidb].[dbo].[estaciones-de-bicicletas-publicas] destino on rr.bici_estacion_destino=destino.nro_est
--WHERE bici_estacion_origen=130
--AND bici_Fecha_hora_retiro BETWEEN '2018-04-27 08:00:00.000' AND '2018-04-27 09:00:00.000'
GROUP BY DATEADD(HOUR, DATEDIFF(HOUR, 0, rr.bici_Fecha_hora_retiro), 0), origen.nombre,rr.bici_estacion_origen
ORDER BY count_origen DESC



SELECT * FROM [pfidb].[dbo].[estaciones-de-bicicletas-publicas] WHERE nro_est=2


SELECT COUNT(*) FROM [pfidb].[dbo].[recorridos-realizados-2018]
WHERE bici_estacion_origen=130 
AND bici_Fecha_hora_retiro BETWEEN '2018-04-27 08:00:00.000' AND '2018-04-27 09:00:00.000'

SELECT COUNT(*) FROM [pfidb].[dbo].[recorridos-realizados-2018]
WHERE bici_estacion_destino=130 
AND bici_Fecha_hora_retiro BETWEEN '2018-04-27 08:00:00.000' AND '2018-04-27 09:00:00.000'