/**
 * Obtiene el ID de un archivo desde el caché seguro (Script Properties)
 * @param {string} nombreArchivo - El nombre del JSON (ej. 'ventas_agrupadas.json')
 * @returns {string|null} El ID del archivo o nulo si no existe
 */
function obtenerIdDesdePropiedades(nombreArchivo) {
  const propiedades = PropertiesService.getScriptProperties();
  const id = propiedades.getProperty(nombreArchivo);

  if (!id) {
    console.error(
      `No se encontró el ID para ${nombreArchivo} en las Propiedades. Ejecuta inicializarEntorno().`,
    );
    return null;
  }
  return id;
}

/**
 * Lee el contenido de un archivo JSON directamente desde Drive usando su ID
 * @param {string} nombreArchivo - El nombre del JSON a leer
 * @returns {Object|null} El objeto JSON parseado
 */
function leerJsonDesdeDrive(nombreArchivo) {
  const idArchivo = obtenerIdDesdePropiedades(nombreArchivo);

  if (!idArchivo) return null;

  try {
    const archivo = DriveApp.getFileById(idArchivo);
    const contenidoTexto = archivo.getBlob().getDataAsString();
    return JSON.parse(contenidoTexto);
  } catch (error) {
    console.error(
      `Error al leer o parsear el archivo ${nombreArchivo}: ${error.message}`,
    );
    return null;
  }
}
