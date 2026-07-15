# Recomendaciones y Modificaciones Críticas

## Consideraciones

Al analizar tu propuesta, identifico algunas áreas técnicas que requieren ajustes para evitar problemas en producción:

1. El límite oculto de la Caché de Apps Script (Muy Importante)
   - El problema: Tienes planeado que el primer usuario cargue los datos en caché para ahorrar cuota. Sin embargo, el CacheService de Google Apps Script tiene un límite estricto de 100 KB por llave/elemento. Un archivo JSON con todas las ventas desglosadas de la empresa superará este límite casi de inmediato, provocando fallos en el script.

   - La solución: Tienes dos opciones. La primera es dividir el JSON en múltiples fragmentos (chunks) menores a 100 KB antes de guardarlos en caché y reensamblarlos al leerlos. La segunda (y más sencilla) es omitir la caché para los archivos de datos. Leer un archivo JSON de texto plano directamente desde Google Drive a través de Apps Script es un proceso extremadamente rápido. Dado que leerás el archivo y luego lo filtrarás en memoria, la penalización de tiempo por leer desde Drive en lugar de la caché será imperceptible para el usuario y te ahorrará problemas de límites de tamaño.

2. Tokens
   - Al generar los tokens en tu script de Python, asegúrate de usar la librería uuid (específicamente uuid.uuid4()) para generar identificadores criptográficamente seguros y difíciles de adivinar (ej. ?token=f47ac10b-58cc-4372-a567-0e02b2c3d479), en lugar de secuencias numéricas o nombres cortos.

3. Paginacion del frontend
   - No programes la paginación desde cero. Te recomiendo integrar una librería ligera como Grid.js o DataTables. Solo necesitas pasarles el objeto JSON de tu fuente de datos desglosada y ellas se encargarán de la paginación, la búsqueda interna y el ordenamiento de columnas de forma automática y con un rendimiento excelente.

## Aplicación

Si leer un json plano es tarea sencilla para la cuota de appscript, pues vayamos por esa ruta.
La realidad es que no todo el tiempo estarán consultando el dashboard los asesores y solo son poco más de 20 en total.
Por lo que entiendo, con esto no será necesario el cache más que entiendo que appscript no puede almacenar en cachce por mucho tiempo de forma "asegurada".

Sobre la seguridad, será embebido en un portal. Entonces no tendrán acceso al link directo, solo lo podrán ver como si fuera un embed de power bi.

Estoy de accuerdo de usar librearias como grid.js para la tabla. no lo habia pensado.
Igual sobre el uuid para crear los tokens.

Sobre la ejecución programada con programador de tareas, pensaba crear un bat file para poder ejecutarlo.
Solo no sé cómo usar typer, entonces no se me ocurre cómo darle un uso. Dejaré eso en tus manos.
El env debe de tener la ruta a mis credenciales de bigquery.
