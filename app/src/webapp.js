/**
 * Punto de entrada principal.
 * Ahora es asíncrono: sirve la interfaz inmediatamente sin hacer cálculos pesados.
 */
function doGet(e) {
  const template = HtmlService.createTemplateFromFile("views/index");

  // Pasamos el token directamente al frontend para que este haga la petición
  template.token = e.parameter.token || "";

  return template
    .evaluate()
    .setTitle(`Dashboard de Ventas`)
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Función invocada desde el navegador (Frontend) usando google.script.run
 * @param {string} token - El token pasado por la URL
 * @returns {Object} Objeto con los datos del asesor o un mensaje de error
 */
function obtenerDatosAsesor(token) {
  if (!token) {
    return { error: "No se proporcionó un token válido en la URL." };
  }

  // 1. Leer la fuente
  const ventasDesglosadas = leerJsonDesdeDrive("ventas_desglosadas.json") || [];

  const propiedades = PropertiesService.getScriptProperties();
  const tokenAdmin = propiedades.getProperty("ADMIN_TOKEN");

  // 2. Validación de Administrador
  if (tokenAdmin && token === tokenAdmin) {
    return {
      asesor: "Administrador General",
      datos: ventasDesglosadas, // Se envía toda la base
    };
  }

  // 3. Validación de Asesor
  const tokensConfig = leerJsonDesdeDrive("config.json");
  if (!tokensConfig) {
    return {
      error: "Error interno: No se pudo cargar la configuración del sistema.",
    };
  }

  let nombreAsesor = null;
  for (const [asesor, asesorToken] of Object.entries(tokensConfig)) {
    if (asesorToken === token) {
      nombreAsesor = asesor;
      break;
    }
  }

  if (!nombreAsesor) {
    return { error: "Acceso denegado: Token inválido o asesor no encontrado." };
  }

  // 4. Filtrado exacto
  const datosFiltrados = ventasDesglosadas.filter(
    (venta) => venta.Asesor === nombreAsesor,
  );

  // Retornar éxito con los datos crudos
  return {
    asesor: nombreAsesor,
    datos: datosFiltrados,
  };
}
