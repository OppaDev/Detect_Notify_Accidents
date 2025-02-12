# Firebase Credentials

En esta carpeta debe ir el archivo de credenciales de Firebase (`firebase-credenciales.json`). Este archivo es necesario para la autenticación del servidor con Firebase.

## Cómo obtener el archivo de credenciales

1. Ve a la [Consola de Firebase](https://console.firebase.google.com/)
2. Selecciona tu proyecto "fallapp-6d506"
3. Ve a Configuración del proyecto (ícono de engranaje)
4. Selecciona la pestaña "Cuentas de servicio"
5. En "SDK Admin de Firebase", haz clic en "Generar nueva clave privada"
6. Guarda el archivo JSON descargado como `firebase-credenciales.json`
7. Coloca el archivo en esta carpeta

## Importante
- NO compartas ni subas este archivo al repositorio
- Mantén este archivo seguro, contiene claves privadas
- Cada desarrollador debe generar sus propias credenciales
