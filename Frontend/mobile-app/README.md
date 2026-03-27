# Aplicación Móvil Flutter

Este proyecto es una aplicación móvil basada en Flutter. Sigue las instrucciones a continuación para configurar tu entorno de desarrollo en Windows o macOS y configurar el desarrollo para Android.

## Primeros Pasos

### 1. Instalar Flutter Manualmente

#### Configuración en Windows
1.  **Instalar Git para Windows**: Descarga e instala la última versión de [Git para Windows](https://git-scm.com/download/win).
2.  **Descargar el SDK de Flutter**: Descarga el último paquete estable del SDK de Flutter desde el [archivo oficial](https://docs.flutter.dev/release/archive/windows).
3.  **Extraer el SDK**:
    *   Crea una carpeta (por ejemplo, `C:\Users\{usuario}\develop`).
    *   Extrae el archivo zip en esa carpeta.
4.  **Actualizar el PATH**:
    *   Ve a **Configuración avanzada del sistema** > **Variables de entorno**.
    *   En **Variables de usuario**, busca o crea `Path`.
    *   Agrega la ruta completa a `flutter\bin` (por ejemplo, `C:\Users\{usuario}\develop\flutter\bin`).
5.  **Verificar**: Abre una nueva terminal y ejecuta:
    ```bash
    flutter --version
    ```

#### Configuración en macOS
1.  **Instalar las herramientas de línea de comandos de Xcode**:
    ```bash
    xcode-select --install
    ```
2.  **Descargar el SDK de Flutter**: Descarga el paquete que coincida con tu CPU (Apple Silicon o Intel) desde el [archivo oficial](https://docs.flutter.dev/release/archive/macos).
3.  **Extraer el SDK**:
    ```bash
    mkdir ~/develop
    unzip ~/Downloads/flutter_macos_3.29.3-stable.zip -d ~/develop/
    ```
4.  **Actualizar el PATH (Zsh)**:
    *   Abre o crea `~/.zprofile`.
    *   Agrega: `export PATH="$HOME/develop/flutter/bin:$PATH"`
    *   Aplica los cambios: `source ~/.zprofile`
5.  **Verificar**: Ejecuta `flutter --version` en tu terminal.

---

### 2. Configurar el Desarrollo para Android

Independientemente de tu sistema operativo, sigue estos pasos para apuntar a Android:

#### Instalar Android Studio
1.  Descarga e instala [Android Studio](https://developer.android.com/studio).
2.  Abre el **SDK Manager** (More Actions > SDK Manager).
3.  En **SDK Platforms**, asegúrate de que esté instalada la última API de Android (por ejemplo, API 36).
4.  En **SDK Tools**, asegúrate de que lo siguiente esté seleccionado e instalado:
    *   Android SDK Build-Tools
    *   Android SDK Command-line Tools
    *   Android Emulator
    *   Android SDK Platform-Tools
    *   CMake
    *   NDK (Side by side)

#### Aceptar Licencias
Ejecuta el siguiente comando y acepta todas las licencias:
```bash
flutter doctor --android-licenses
```

#### Configurar un Dispositivo Android
*   **Emulador**: Abre el **Device Manager** en Android Studio, haz clic en **Create Virtual Device**, selecciona un perfil de hardware y una imagen de sistema (x86_64 para Intel/AMD, ARM64 para Apple Silicon), y finaliza la configuración.
*   **Dispositivo Físico**: Habilita las **Opciones de desarrollador** y la **Depuración por USB** en tu dispositivo Android, luego conéctalo vía USB.

---

### 3. Validar la Configuración

Ejecuta el siguiente comando para verificar si faltan dependencias:
```bash
flutter doctor
```

Verifica que tus dispositivos sean reconocidos:
```bash
flutter devices
```

---

### 4. Ejecutar la Aplicación

Una vez configurado el entorno:

1.  Navega al directorio del proyecto:
    ```bash
    cd Frontend/mobile-app
    ```
2.  Obtén las dependencias:
    ```bash
    flutter pub get
    ```
3.  Ejecuta la aplicación:
    ```bash
    flutter run
    ```

## Estructura del Proyecto
- `lib/`: Contiene el código fuente en Dart.
- `test/`: Contiene las pruebas unitarias y de widgets.
- `android/`: Configuración específica para Android.
- `ios/`: Contiene la configuración para iOS.

## CI/CD y Firmado de Aplicación
Este proyecto incluye un flujo de trabajo automatizado con **GitHub Actions** para la integración continua (CI).

- **CI Workflow**: Se encuentra en `.github/workflows/android_ci.yml`. Realiza análisis estático, ejecución de pruebas y validación de compilación en cada Pull Request.
- **Guía de Firmado**: Para configurar el firmado de la aplicación en el pipeline de CI, consulta la [Guía de Firmado de Android](docs/guia_firmado_android.md).
- **Verificación Local**: Puedes ejecutar el script `scripts/verify_ci_locally.sh` para validar que tu código pase todas las etapas de CI antes de subirlo al repositorio.
