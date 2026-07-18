/**
 * EJECUTAR ESTA FUNCIÓN MANUALMENTE DESDE EL EDITOR DE APPS SCRIPT UNA SOLA VEZ.
 * Escanea la carpeta (cuyo ID está en las Propiedades) y guarda los IDs de los JSON.
 */
function inicializarEntorno() {
  const propiedades = PropertiesService.getScriptProperties();

  // 1. Leer el ID de la carpeta desde el almacenamiento seguro
  const carpetaId = propiedades.getProperty("CARPETA_DRIVE_ID");

  if (!carpetaId) {
    Logger.log(
      "❌ Error: No se encontró CARPETA_DRIVE_ID en las Propiedades del Script.",
    );
    return;
  }

  const carpeta = DriveApp.getFolderById(carpetaId);

  // 2. Nombres exactos de los archivos generados por Python
  const archivosRequeridos = ["ventas_desglosadas.json", "config.json"];

  // 3. Buscar y guardar los IDs de los archivos
  archivosRequeridos.forEach((nombreArchivo) => {
    const iteradorArchivos = carpeta.getFilesByName(nombreArchivo);

    if (iteradorArchivos.hasNext()) {
      const archivo = iteradorArchivos.next();
      propiedades.setProperty(nombreArchivo, archivo.getId());
      Logger.log(
        `✅ Éxito: Guardado ID para ${nombreArchivo} -> ${archivo.getId()}`,
      );
    } else {
      Logger.log(
        `❌ Error: No se encontró el archivo ${nombreArchivo} en la carpeta.`,
      );
    }
  });
}
