# Firebase Credentials

En esta carpeta debe ir el archivo JSON de las credenciales de Firebase. Este archivo es necesario para que la aplicación pueda comunicarse con los servicios de Firebase.

## Cómo obtener el archivo JSON de Firebase

1. Ve a la [Consola de Firebase](https://console.firebase.google.com/).
2. Selecciona tu proyecto.
3. En el panel de navegación, haz clic en el ícono de engranaje junto a "Project Overview" y selecciona "Project settings".
4. En la pestaña "General", desplázate hacia abajo hasta la sección "Your apps".
5. Si aún no has agregado tu aplicación, haz clic en "Add app" y sigue las instrucciones para registrarla.
6. Una vez registrada la aplicación, haz clic en "Download google-services.json" para descargar el archivo JSON de configuración.

Coloca el archivo `google-services.json` en esta carpeta (`/c:/Users/OppaDev/Desktop/DataSets/AppFallDetectV1/Back/app/core/credentials/`).

Asegúrate de no compartir este archivo públicamente, ya que contiene información sensible de tu proyecto de Firebase.
## Nota Importante

Este archivo no se incluye en el repositorio por razones de seguridad. Cada desarrollador debe obtener su propio archivo `google-services.json` siguiendo las instrucciones anteriores.