WITH Ventas_Portal_Asesores AS (
  SELECT
    TRIM(CONCAT(ext.DesarrolloLargo, ' ', ext.Unidad)) AS id,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) AS Asesor,
    d.Marca, ext.Desarrollo,
    NULLIF(TRIM(ext.Privada), 'N/A') AS Privada,
    NULLIF(TRIM(ext.Etapa), 'N/A') AS Etapa, ext.Unidad,
    NULLIF(INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Asesor), NFKD),r'\pM', '')) , 'N/A') AS Modelo,
    ext.M2, ext.PrecioM2, ext.PrecioVenta,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.Cliente), NFKD),r'\pM', '')) AS Cliente,
    ext.FechaProceso, ext.FechaFinalizado,
    INITCAP(REGEXP_REPLACE(NORMALIZE(TRIM(ext.EstatusVenta), NFKD),r'\pM', '')) AS EstatusVenta,
    ext.Estatus
  FROM EXTERNAL_QUERY("terraviva-439415.us.dam", """
    SELECT
      v.id_venta,
      v.numero_acciones AS M2,
      v.aportacion_accion AS PrecioM2,
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
),
Ventas_Clasificadas AS (
  SELECT
    Asesor, Marca, Desarrollo,
    id, PrecioVenta,
    CASE 
      WHEN Estatus IN (7, 8) THEN 'Finalizado'
      WHEN Estatus NOT IN (1, 7, 8) THEN 'Proceso'
    END AS Estatus,
    CASE 
      WHEN Estatus IN (7, 8) THEN DATE_TRUNC(FechaFinalizado, MONTH)
      WHEN Estatus NOT IN (1, 7, 8) THEN DATE_TRUNC(FechaProceso, MONTH)
    END AS FechaMesAnio
  FROM Ventas_Portal_Asesores
)
SELECT
  Asesor, Marca, Desarrollo,
  COUNT(DISTINCT id) AS Unidades,
  SUM(PrecioVenta) AS PrecioVenta,
  FechaMesAnio, Estatus
FROM Ventas_Clasificadas
WHERE FechaMesAnio IS NOT NULL
GROUP BY Asesor, Marca, Desarrollo, FechaMesAnio, Estatus
ORDER BY Asesor ASC, Marca ASC, Desarrollo ASC, FechaMesAnio DESC;