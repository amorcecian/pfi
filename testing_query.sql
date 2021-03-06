--Adding a station to a full cluster to analyze its variation
-- DELETE FROM [dbo].[estaciones-de-bicicletas-publicas] WHERE nro_est=400
-- INSERT INTO [dbo].[estaciones-de-bicicletas-publicas] 
-- VALUES (-58.373857,-34.595029,'Test para variar clusters','Pepito 123',400,'PEPITO 123',100)

DELETE FROM [dbo].[stations_with_centroids] WHERE nro_est=400
DELETE FROM [dbo].[estaciones-de-bicicletas-publicas] WHERE nro_est=400


SELECT * FROM [dbo].[estaciones-de-bicicletas-publicas]

INSERT INTO [dbo].[estaciones-de-bicicletas-publicas] 
VALUES (-58.362112,-34.614567,'Test para variar clusters','Pepito 123',400,'PEPITO 123',100)


-- Adding new stations far away from the others
DELETE FROM [dbo].[estaciones-de-bicicletas-publicas] WHERE nro_est=300
INSERT INTO [dbo].[estaciones-de-bicicletas-publicas] 
VALUES (-58.469174,-34.53864,'Test','Calle Falsa 123',300,'CALLE FALSA 123',10)