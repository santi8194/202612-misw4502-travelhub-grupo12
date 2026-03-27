# Gestión de Almacén de Claves (Keystore) de Android para Travel Hub Mobile

Esta guía explica cómo generar un almacén de claves (keystore) para la firma de versiones de lanzamiento en Android y cómo configurarlo para el flujo de trabajo de CI/CD en GitHub Actions.

## 1. Generar un Almacén de Claves (Keystore)

Ejecuta el siguiente comando en tu terminal para generar un archivo de almacén de claves.

### Valores Sugeridos:
Para facilitar la configuración, se sugieren los siguientes valores:
- **Nombre del archivo**: `travel_hub_release.jks`
- **Keystore Password**: `TravelHub123!` (o una frase segura)
- **Alias de la llave**: `travel_hub_alias`
- **Key Password**: `TravelHub123!` (se recomienda la misma que el keystore)

### Comando de ejemplo:
```bash
keytool -genkey -v -keystore travel_hub_release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias travel_hub_alias
```

Se te pedirá que ingreses contraseñas y detalles de la organización. **¡Mantén estas contraseñas en un lugar seguro!**

## 2. Configuración de Secretos en GitHub

Para permitir que el flujo de CI/CD firme tu APK de lanzamiento, debes agregar los siguientes **Secretos del Repositorio** en la configuración de tu repositorio de GitHub (`Settings > Secrets and variables > Actions`):

1. **`ANDROID_KEYSTORE_BASE64`**: La cadena codificada en base64 de tu archivo `.jks`.
   - Para codificar en macOS/Linux: `base64 -i travel_hub_release.jks | pbcopy`
   - Para codificar en Windows (PowerShell): `[Convert]::ToBase64String([IO.File]::ReadAllBytes("travel_hub_release.jks"))`
2. **`ANDROID_KEYSTORE_PASSWORD`**: La contraseña de tu almacén de claves.
3. **`ANDROID_KEY_ALIAS`**: El alias que utilizaste durante la generación.
4. **`ANDROID_KEY_PASSWORD`**: La contraseña para la llave específica (generalmente es la misma que la del almacén de claves).

## 3. Integración con el Flujo de Trabajo de CI/CD

El flujo de trabajo en `.github/workflows/android_ci.yml` está configurado para compilar el APK automáticamente. Utiliza las variables de entorno que el sistema de construcción de Android espera.

### Ubicación del Flujo de Trabajo
Al tratarse de un monorepositorio, el flujo de trabajo se encuentra en la raíz: `.github/workflows/android_ci.yml`.

### Lógica Actual en `build.gradle.kts`:
El proyecto en `Frontend/mobile-app/android/app/build.gradle.kts` ya está configurado para verificar las siguientes variables de entorno:
- `ANDROID_KEYSTORE_PATH`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`

Si estas no están presentes, el sistema utiliza por defecto la configuración de firma de depuración (debug), permitiendo que el desarrollo local continúe sin interrupciones.
