## Por qué el archivo .env no se sube al repositorio

El archivo `.env` contiene variables de entorno que a menudo se utilizan para almacenar información sensible, como claves de API, credenciales de bases de datos y otros ajustes de configuración. Para garantizar la seguridad y privacidad de esta información sensible, el archivo `.env` generalmente se agrega al archivo `.gitignore`, lo que impide que sea rastreado y subido al repositorio.

Al no incluir el archivo `.env` en el repositorio, reducimos el riesgo de exponer información sensible a usuarios no autorizados. En su lugar, cada desarrollador o entorno de despliegue debe mantener su propio archivo `.env` con los ajustes de configuración necesarios.

Para configurar las variables de entorno, puedes crear un archivo `.env` en el directorio raíz del proyecto y agregar las variables requeridas en el siguiente formato:

# Firebase Configuration
FIREBASE_CRED_PATH=
FIREBASE_DATABASE_URL=
# Detection Configuration
DETECTION_THRESHOLD=
NOTIFICATION_COOLDOWN=

# App Configuration
APP_NAME=
DEBUG=True
API_V1_STR=
CAMERA_URL=
