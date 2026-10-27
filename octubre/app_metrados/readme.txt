Para respaldar o reconstruir esta app en el futuro sin tener que guardar todo el
proyecto pesado (que contiene carpetas temporales como build o .gradle), solo
necesitas conservar 5 archivos clave:

1. MetradoModel.kt (El Modelo de Datos)

  - Ubicación: app/src/main/java/com/example/metradosapp/model/MetradoModel.kt
  - Por qué es importante: Contiene la estructura de la Norma Peruana
    (PartidaMetrado, DetalleCalculo) y la fórmula matemática del cálculo de
    parciales (L \times A \times H \times Veces). Es la base que define cómo se
    organiza el JSON.

2. MetradoViewModel.kt (La Lógica del Negocio)

  - Ubicación:
    app/src/main/java/com/example/metradosapp/viewmodel/MetradoViewModel.kt
  - Por qué es importante:
      - Maneja las operaciones CRUD (crear, editar, eliminar metrados).
      - Contiene el algoritmo que convierte los objetos Kotlin a archivo JSON y
        lanza el menú para compartirlo por WhatsApp, Drive o Correo.

3. MainActivity.kt (La Interfaz de Usuario)

  - Ubicación: app/src/main/java/com/example/metradosapp/MainActivity.kt
  - Por qué es importante: Es toda la interfaz visual hecha en Jetpack Compose:
    el formulario de entrada de medidas, el botón dinámico (Guardar /
    Actualizar), la lista en tiempo real y las llamadas a los eventos del
    ViewModel.

4. build.gradle.kts del Módulo App (Las Dependencias)

  - Ubicación: app/build.gradle.kts
  - Por qué es importante: Guarda las versiones exactas y compatibles de las
    librerías externas que hacen funcionar el proyecto:
      - com.google.code.gson:gson (Serialización JSON).
      - androidx.lifecycle:lifecycle-viewmodel-compose (Controlador de estado).
      - androidx.compose.material:material-icons-extended (Iconos de editar y
        borrar).
      - El BOM de Compose para evitar incompatibilidades.

5. AndroidManifest.xml y file_paths.xml (Permisos del Sistema)

  - Ubicaciones:
      - app/src/main/AndroidManifest.xml
      - app/src/main/res/xml/file_paths.xml
  - Por qué son importantes: Contienen la configuración del FileProvider. Sin
    estos dos archivos, Android bloqueará la exportación del JSON por políticas
    de seguridad de almacenamiento.
