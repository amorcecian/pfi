CREATE TABLE "estaciones-de-bicicletas-publicas" (
    lat FLOAT,
    long FLOAT,
    nombre NVARCHAR(50),
    domicilio NVARCHAR(512),
    nro_est INT primary key,
    dire_norm NVARCHAR(50)
)