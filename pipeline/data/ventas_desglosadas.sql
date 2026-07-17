WITH Ventas_Portal_Asesores AS (
-- Terraviva
  SELECT
    TRIM(CONCAT(ext.DesarrolloLargo, ' ', ext.Unidad)) AS id,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) AS Asesor,
    d.Marca, ext.Desarrollo,
    NULLIF(TRIM(ext.Privada), 'N/A') AS Privada,
    NULLIF(TRIM(ext.Etapa), 'N/A') AS Etapa, ext.Unidad,
    NULLIF(INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) , 'N/A') AS Modelo,
    ext.M2, SAFE_DIVIDE(ext.PrecioVenta, ext.M2) AS PrecioM2, ext.PrecioVenta,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Cliente), NFKD),r'\pM', '')) AS Cliente,
    ext.FechaProceso, ext.FechaFinalizado,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.EstatusVenta), NFKD),r'\pM', '')) AS EstatusVenta,
    ext.Estatus
  FROM EXTERNAL_QUERY("terraviva-439415.us.terraviva", """
    SELECT
      v.id_venta,
      v.precio_venta AS PrecioVenta,
      DATE(NULLIF(v.fecha_venta, '0000-00-00')) AS FechaProceso,
      DATE(NULLIF(v.fecha_cierre_venta, '0000-00-00')) AS FechaFinalizado,
      d.nombre_desarrollo AS DesarrolloLargo,
      dc.nombre_comercial AS Desarrollo,
      uni.privada AS Privada,
      uni.numero_etapa AS Etapa,
      uni.numero_unidad AS Unidad,
      uni.modelo AS Modelo,
      uni.metros_cuadrados_totales AS M2,
      CONCAT_WS(' ', c.nombre, c.apellido_p, c.apellido_m) AS Cliente,
      CONCAT_WS(' ', u.nombre, u.apellido_paterno, u.apellido_materno) AS Asesor,
      sv.nombre AS EstatusVenta,
      v.status_venta AS Estatus
    FROM venta AS v
    LEFT JOIN unidades AS uni ON v.id_unidad = uni.id_unidad
    LEFT JOIN desarrollo AS d ON uni.id_desarrollo = d.id_desarrollo
    LEFT JOIN desarrollo_comercial AS dc ON d.id_desarrollo_comercial = dc.id_desarrollo_comercial
    LEFT JOIN status_venta AS sv ON v.status_venta = sv.id_status
    LEFT JOIN cliente AS c ON v.id_cliente = c.id_cliente
    LEFT JOIN usuario AS u ON v.id_usuario = u.id_usuario
    WHERE dc.nombre_comercial IS NOT NULL
      AND dc.nombre_comercial <> 'Demo Manivela'
  """) AS ext
  LEFT JOIN `Dimensiones.Desarrollos` AS d ON ext.Desarrollo = d.Desarrollo

-- DAM
  UNION ALL
  SELECT
    TRIM(CONCAT(ext.DesarrolloLargo, ' ', ext.Unidad)) AS id,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) AS Asesor,
    d.Marca, ext.Desarrollo,
    NULLIF(TRIM(ext.Privada), 'N/A') AS Privada,
    NULLIF(TRIM(ext.Etapa), 'N/A') AS Etapa, ext.Unidad,
    NULLIF(INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) , 'N/A') AS Modelo,
    ext.M2, SAFE_DIVIDE(ext.PrecioVenta, ext.M2) AS PrecioM2, ext.PrecioVenta,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Cliente), NFKD),r'\pM', '')) AS Cliente,
    ext.FechaProceso, ext.FechaFinalizado,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.EstatusVenta), NFKD),r'\pM', '')) AS EstatusVenta,
    ext.Estatus
  FROM EXTERNAL_QUERY("terraviva-439415.us.dam", """
    SELECT
      v.id_venta,
      v.numero_acciones AS M2,
      v.precio_venta AS PrecioVenta,
      DATE(NULLIF(v.fecha_venta, '0000-00-00')) AS FechaProceso,
      DATE(NULLIF(v.fecha_cierre_venta, '0000-00-00')) AS FechaFinalizado,
      d.nombre_desarrollo AS DesarrolloLargo,
      dc.nombre_comercial AS Desarrollo,
      uni.privada AS Privada,
      uni.numero_etapa AS Etapa,
      uni.numero_unidad AS Unidad,
      uni.modelo AS Modelo,
      CONCAT_WS(' ', c.nombre, c.apellido_p, c.apellido_m) AS Cliente,
      CONCAT_WS(' ', u.nombre, u.apellido_paterno, u.apellido_materno) AS Asesor,
      sv.nombre AS EstatusVenta,
      v.status_venta AS Estatus
    FROM venta AS v
    LEFT JOIN unidades AS uni ON v.id_unidad = uni.id_unidad
    LEFT JOIN desarrollo AS d ON uni.id_desarrollo = d.id_desarrollo
    LEFT JOIN desarrollo_comercial AS dc ON d.id_desarrollo_comercial = dc.id_desarrollo_comercial
    LEFT JOIN status_venta AS sv ON v.status_venta = sv.id_status
    LEFT JOIN cliente AS c ON v.id_cliente = c.id_cliente
    LEFT JOIN usuario AS u ON v.id_usuario = u.id_usuario
    WHERE dc.nombre_comercial IS NOT NULL
      AND dc.nombre_comercial <> 'Demo Manivela'
  """) AS ext
  LEFT JOIN `Dimensiones.Desarrollos` AS d ON ext.Desarrollo = d.Desarrollo

-- Custo
  UNION ALL
  SELECT
    TRIM(CONCAT(ext.DesarrolloLargo, ' ', ext.Unidad)) AS id,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) AS Asesor,
    d.Marca, ext.Desarrollo,
    NULLIF(TRIM(ext.Privada), 'N/A') AS Privada,
    NULLIF(TRIM(ext.Etapa), 'N/A') AS Etapa, ext.Unidad,
    NULLIF(INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) , 'N/A') AS Modelo,
    ext.M2, SAFE_DIVIDE(ext.PrecioVenta, ext.M2) AS PrecioM2, ext.PrecioVenta,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Cliente), NFKD),r'\pM', '')) AS Cliente,
    ext.FechaProceso, ext.FechaFinalizado,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.EstatusVenta), NFKD),r'\pM', '')) AS EstatusVenta,
    ext.Estatus
  FROM EXTERNAL_QUERY("terraviva-439415.us.dam", """
    SELECT
      v.id_venta,
      v.precio_venta AS PrecioVenta,
      DATE(NULLIF(v.fecha_venta, '0000-00-00')) AS FechaProceso,
      DATE(NULLIF(v.fecha_cierre_venta, '0000-00-00')) AS FechaFinalizado,
      d.nombre_desarrollo AS DesarrolloLargo,
      dc.nombre_comercial AS Desarrollo,
      uni.privada AS Privada,
      uni.numero_etapa AS Etapa,
      uni.numero_unidad AS Unidad,
      uni.modelo AS Modelo,
      uni.metros_cuadrados_totales AS M2,
      CONCAT_WS(' ', c.nombre, c.apellido_p, c.apellido_m) AS Cliente,
      CONCAT_WS(' ', u.nombre, u.apellido_paterno, u.apellido_materno) AS Asesor,
      sv.nombre AS EstatusVenta,
      v.status_venta AS Estatus
    FROM venta AS v
    LEFT JOIN unidades AS uni ON v.id_unidad = uni.id_unidad
    LEFT JOIN desarrollo AS d ON uni.id_desarrollo = d.id_desarrollo
    LEFT JOIN desarrollo_comercial AS dc ON d.id_desarrollo_comercial = dc.id_desarrollo_comercial
    LEFT JOIN status_venta AS sv ON v.status_venta = sv.id_status
    LEFT JOIN cliente AS c ON v.id_cliente = c.id_cliente
    LEFT JOIN usuario AS u ON v.id_usuario = u.id_usuario
    WHERE dc.nombre_comercial IS NOT NULL
      AND dc.nombre_comercial <> 'Demo Manivela'
  """) AS ext
  LEFT JOIN `Dimensiones.Desarrollos` AS d ON ext.Desarrollo = d.Desarrollo

-- Almaviva
  UNION ALL
  SELECT
    TRIM(CONCAT(ext.DesarrolloLargo, ' ', ext.Unidad)) AS id,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) AS Asesor,
    d.Marca, ext.Desarrollo,
    NULLIF(TRIM(ext.Privada), 'N/A') AS Privada,
    NULLIF(TRIM(ext.Etapa), 'N/A') AS Etapa, ext.Unidad,
    NULLIF(INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) , 'N/A') AS Modelo,
    ext.M2, SAFE_DIVIDE(ext.PrecioVenta, ext.M2) AS PrecioM2, ext.PrecioVenta,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Cliente), NFKD),r'\pM', '')) AS Cliente,
    ext.FechaProceso, ext.FechaFinalizado,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.EstatusVenta), NFKD),r'\pM', '')) AS EstatusVenta,
    ext.Estatus
  FROM EXTERNAL_QUERY("terraviva-439415.us.dam", """
    SELECT
      v.id_venta,
      v.precio_venta AS PrecioVenta,
      DATE(NULLIF(v.fecha_venta, '0000-00-00')) AS FechaProceso,
      DATE(NULLIF(v.fecha_cierre_venta, '0000-00-00')) AS FechaFinalizado,
      d.nombre_desarrollo AS DesarrolloLargo,
      dc.nombre_comercial AS Desarrollo,
      uni.privada AS Privada,
      uni.numero_etapa AS Etapa,
      uni.numero_unidad AS Unidad,
      uni.modelo AS Modelo,
      uni.metros_cuadrados_totales AS M2,
      CONCAT_WS(' ', c.nombre, c.apellido_p, c.apellido_m) AS Cliente,
      CONCAT_WS(' ', u.nombre, u.apellido_paterno, u.apellido_materno) AS Asesor,
      sv.nombre AS EstatusVenta,
      v.status_venta AS Estatus
    FROM venta AS v
    LEFT JOIN unidades AS uni ON v.id_unidad = uni.id_unidad
    LEFT JOIN desarrollo AS d ON uni.id_desarrollo = d.id_desarrollo
    LEFT JOIN desarrollo_comercial AS dc ON d.id_desarrollo_comercial = dc.id_desarrollo_comercial
    LEFT JOIN status_venta AS sv ON v.status_venta = sv.id_status
    LEFT JOIN cliente AS c ON v.id_cliente = c.id_cliente
    LEFT JOIN usuario AS u ON v.id_usuario = u.id_usuario
    WHERE dc.nombre_comercial IS NOT NULL
      AND dc.nombre_comercial <> 'Demo Manivela'
  """) AS ext
  LEFT JOIN `Dimensiones.Desarrollos` AS d ON ext.Desarrollo = d.Desarrollo
)
SELECT * EXCEPT(id, Estatus) FROM Ventas_Portal_Asesores
WHERE FechaProceso >= DATE_SUB(
  DATE_TRUNC(CURRENT_DATE("America/Merida"), YEAR), 
  INTERVAL 1 MONTH
)
AND Asesor IN (
  -- Liliana Reyes
  "Carlos Gonzalez", "Carmen Palay", "Daniela Prada", "Fabiola Pardenilla", "Jennifer Barrios",
  "Jorge Alamilla", "Eduardo Cervera", "Manuel Gomez", "Mariana Alcala", "Fernanda Sosa",
  "Alejandro Arzapalo", "Elide Canul", "Victor Barrera", "Yesica Escamilla",

  -- Mauricio Tager
  "Enrique Cossi", "David Guemez", "Erika Buenfil", "Fatima Dommerque", "Gabriela Fernandez",
  "Gabriela Zapata", "Jorge Erosa", "Jorgeandres Perez", "Mariel Chan", "Lucia Esqueda",
  "Rafael Gamboa", "Tomas Medina", "Yolidavey Santiago", "Genesis Moreno",

  -- Fernando Soriano
  "Ivonne Urbina", "Vania Carbajal", "Adrian Blasio", "Alejandro Rodriguez", "Samantha Cortes",
  "Diego Suarez", "Jorge Flores", "Antonio Fabila", "Alan Guerrero", "Priscila Mota",
  "Enrique Acevedo",

  -- Inmobiliarias
  "Caribe Inversiones", "Team Jerry Medina", "Grupo Raices", "Hogar 3-51", "Alfa Real Estate",
  "Nativo Master Brokers", "Genesis Sosa", "Franklin Canul", "Antoka", "Victor Gamboa",
  "Daniela Rivas"
)
ORDER BY Asesor ASC, Marca ASC, Desarrollo ASC, FechaProceso DESC