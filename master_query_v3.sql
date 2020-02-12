WITH estaciones_origen AS
(
SELECT DATEADD(HOUR, DATEDIFF(HOUR, 0, rr.bici_Fecha_hora_retiro), 0) AS bici_Fecha_hora_retiro_aux, --origen.nombre, 
rr.bici_estacion_origen ,COUNT(rr.bici_estacion_origen) AS count_origen
FROM [recorridos-realizados-2018] rr
--INNER JOIN [EcoBici].[dbo].[estaciones-de-bicicletas-publicas] origen on rr.bici_estacion_origen=origen.nro_est
--WHERE bici_estacion_origen=130
--AND bici_Fecha_hora_retiro BETWEEN '2018-04-27 08:00:00.000' AND '2018-04-27 09:00:00.000'
GROUP BY DATEADD(HOUR, DATEDIFF(HOUR, 0, rr.bici_Fecha_hora_retiro), 0),rr.bici_estacion_origen--, origen.nombre
--ORDER BY count_origen DESC
),
estaciones_destino AS
(
SELECT bici_estacion_destino, return_datetime, COUNT(bici_estacion_destino) count_destino 
FROM (
	SELECT bici_estacion_destino
	,DATEPART(mi,bici_tiempo_uso) AS min_of_usage
	,CASE
		WHEN DATEPART(mi,bici_tiempo_uso) < 10 THEN (DATEADD(HOUR, DATEDIFF(HOUR, 0, CAST(CONVERT(date,bici_Fecha_hora_retiro) AS datetime) + CAST(DATEADD(MI, DATEDIFF(MI, 8, bici_Fecha_hora_retiro), bici_tiempo_uso) AS datetime) ), 0))
		WHEN DATEPART(mi,bici_tiempo_uso) > 10 THEN DATEADD(HOUR, 1, (DATEADD(HOUR, DATEDIFF(HOUR, 0, CAST(CONVERT(date,bici_Fecha_hora_retiro) AS datetime) + CAST(DATEADD(MI, DATEDIFF(MI, 8, bici_Fecha_hora_retiro), bici_tiempo_uso) AS datetime) ), 0)))
		ELSE [bici_Fecha_hora_retiro]
	END AS return_datetime
	FROM [recorridos-realizados-2018]
	WHERE [bici_tiempo_uso] IS NOT NULL) as aux_table
GROUP BY bici_estacion_destino, return_datetime
--ORDER BY count_destino DESC
)

SELECT estaciones.nombre, estaciones.nro_est, estaciones.lat, estaciones.long
, origen.bici_Fecha_hora_retiro_aux, destino.return_datetime, origen.count_origen,destino.count_destino
, (destino.count_destino-origen.count_origen) AS diferencia
, estaciones.capacidad
FROM estaciones_origen origen
INNER JOIN estaciones_destino destino ON origen.bici_estacion_origen=destino.bici_estacion_destino
AND origen.bici_Fecha_hora_retiro_aux=destino.return_datetime
INNER JOIN [estaciones-de-bicicletas-publicas] estaciones ON estaciones.nro_est=origen.bici_estacion_origen
ORDER BY diferencia DESC