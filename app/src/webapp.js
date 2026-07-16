/**
 * Punto de entrada principal de la Web App.
 * Se ejecuta cuando un usuario o un iframe accede a la URL publicada.
 */
function doGet(e) {
  // Extraer el token de los parámetros de la URL (?token=...)
  const token = e.parameter.token;

  if (!token) {
    return mostrarError(
      "Acceso denegado: No se proporcionó un token válido en la URL.",
    );
  }

  // 1. Cargar las fuentes de datos desde Drive
  const ventasAgrupadas = leerJsonDesdeDrive("ventas_agrupadas.json") || [];
  const ventasDesglosadas = leerJsonDesdeDrive("ventas_desglosadas.json") || [];

  // 2. Verificar si el token proporcionado es el Token Maestro
  const propiedades = PropertiesService.getScriptProperties();
  const tokenAdmin = propiedades.getProperty("ADMIN_TOKEN");

  let nombreAsesor = null;
  let datosAsesorAgrupados = [];
  let datosAsesorDesglosados = [];

  if (tokenAdmin && token === tokenAdmin) {
    // Flujo de Administrador: Se asigna un nombre genérico y NO se filtran los datos
    nombreAsesor = "Administrador General";
    datosAsesorAgrupados = ventasAgrupadas;
    datosAsesorDesglosados = ventasDesglosadas;
  } else {
    // Flujo de Asesor: Se busca el token en config.json
    const tokensConfig = leerJsonDesdeDrive("config.json");
    if (!tokensConfig) {
      return mostrarError(
        "Error interno: No se pudo cargar la configuración del sistema.",
      );
    }

    for (const [asesor, asesorToken] of Object.entries(tokensConfig)) {
      if (asesorToken === token) {
        nombreAsesor = asesor;
        break;
      }
    }

    if (!nombreAsesor) {
      return mostrarError(
        "Acceso denegado: No se proporcionó un token válido en la URL.",
      );
    }

    // Filtrar los datos exclusivamente para el asesor validado
    datosAsesorAgrupados = ventasAgrupadas.filter(
      (venta) => venta.Asesor === nombreAsesor,
    );
    datosAsesorDesglosados = ventasDesglosadas.filter(
      (venta) => venta.Asesor === nombreAsesor,
    );
  }

  // 3. Construir la vista HTML
  const template = HtmlService.createTemplateFromFile("views/index");
  template.asesor = nombreAsesor;
  template.datosAgrupados = JSON.stringify(datosAsesorAgrupados);
  template.datosDesglosados = JSON.stringify(datosAsesorDesglosados);

  // 4. Servir la página con permisos para ser embebida
  return template
    .evaluate()
    .setTitle(`Dashboard de Ventas - ${nombreAsesor}`)
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Retorna una vista simple de error en caso de fallo de autenticación.
 */
function mostrarError(mensaje) {
  return HtmlService.createHtmlOutput(`
    <div style="font-family: sans-serif; text-align: center; padding: 50px;">
      <h2 style="color: #d32f2f;">Error de Acceso</h2>
      <p>${mensaje}</p>
    </div>
  `);
}
