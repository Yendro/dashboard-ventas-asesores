# Almacenamiento de datos en carpeta de Drive

## Paso previo para sobreescribir los archivos

Detecté que para poder usar el servicio de google con su api de Drive, tengo que tener una cuenta workspace.  
Por el momento, resolví el problema de la conexión de google subiendo primero los archivos de output/ a la carpeta y luego dejar que el script simplemente los sobreescriba.  
Esto permitió la funcionalidad del script sin hacer modificaciones.

Ahora, podemos proceder con el consumo de los datos en la app web.

## Configuración de los archivos en la app

Sobre los archivos, entiendo que tienen su propio id en drive. Pero si los sobreescribe el script de python no se cambia el id con cada ejecución?

De igual forma, me gustaría no tener expuesto los id de archivos en. Si bien no hay un .env, podemos hacer uso de almacenamiento en las Propiedades de las secuencias de comandos.  
Sería muy bueno poder analizar la carpeta de drive completamente, que la app adquiera los id de los archivos que tienen el nombre de los json y que los almacene en las Propiedades de las secuencias de comandos. Así sería solo configurar el id de la carpeta y el resto lo hace el backend.  
Puedes hacer mención o recomendaciones de este enfoque igual, ya que sería primera vez que le doy uso a este apartado de appscript.

# Modificacion

1. Guardar el ID de la Carpeta Manualmente
   Dado que es un solo ID que no cambiará, la forma más limpia es inyectarlo directamente desde la interfaz de Apps Script, sin siquiera escribirlo en el código de VS Code:

Abre tu proyecto en el editor web de Google Apps Script.

En el menú de la izquierda, haz clic en el icono del engranaje (Configuración del proyecto).

Desplázate hacia abajo hasta Propiedades de la secuencia de comandos y haz clic en Añadir propiedad de la secuencia de comandos.

Escribe CARPETA_DRIVE_ID en el campo Propiedad y pega el ID de tu carpeta compartida en Valor.

Guarda los cambios.
