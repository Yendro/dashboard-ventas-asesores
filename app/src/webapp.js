/**
 * Punto de entrada principal de la Web App.
 * Se ejecuta cuando un usuario o un iframe accede a la URL publicada.
 */
function doGet(e) {
  // 1. Extraer el token de los parámetros de la URL (?token=...)
  const token = e.parameter.token;

  if (!token) {
    return mostrarError(
      "Acceso denegado: No se proporcionó un token en la URL.",
    );
  }

  // 2. Validar el token y obtener el nombre del asesor
  const tokensConfig = leerJsonDesdeDrive("config.json");
  if (!tokensConfig) {
    return mostrarError(
      "Error interno: No se pudo cargar la configuración del sistema.",
    );
  }

  let nombreAsesor = null;
  // tokensConfig es un objeto tipo { "Yendri": "uuid-123", "Ivan": "uuid-456" }
  // Lo recorremos para encontrar a quién le pertenece el token ingresado
  for (const [asesor, asesorToken] of Object.entries(tokensConfig)) {
    if (asesorToken === token) {
      nombreAsesor = asesor;
      break;
    }
  }

  if (!nombreAsesor) {
    return mostrarError(
      "Acceso denegado: Token inválido o asesor no encontrado.",
    );
  }

  // 3. Cargar las fuentes de datos desde Drive
  const ventasAgrupadas = leerJsonDesdeDrive("ventas_agrupadas.json") || [];
  const ventasDesglosadas = leerJsonDesdeDrive("ventas_desglosadas.json") || [];

  // 4. Filtrar los datos exclusivamente para el asesor validado
  const datosAsesorAgrupados = ventasAgrupadas.filter(
    (venta) => venta.Asesor === nombreAsesor,
  );
  const datosAsesorDesglosados = ventasDesglosadas.filter(
    (venta) => venta.Asesor === nombreAsesor,
  );

  // 5. Construir la vista HTML
  const template = HtmlService.createTemplateFromFile("views/index");

  // Inyectar los datos filtrados directamente en el template HTML
  template.asesor = nombreAsesor;
  template.datosAgrupados = JSON.stringify(datosAsesorAgrupados);
  template.datosDesglosados = JSON.stringify(datosAsesorDesglosados);

  // 6. Servir la página con permisos para ser embebida
  return (
    template
      .evaluate()
      .setTitle(`Dashboard de Ventas - ${nombreAsesor}`)
      .addMetaTag("viewport", "width=device-width, initial-scale=1")
      // ¡CRÍTICO! Esto permite que la app se incruste en iframes de otros dominios
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
  );
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
