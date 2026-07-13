# Sistema de Gestión de Inventario y Créditos - Carnicería

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu equipo:
* Python 3.10 o superior
* PostgreSQL (junto con pgAdmin 4 para la administración visual)
* Git (para clonar el repositorio)

---

## Paso 1: Configurar la Base de Datos en PostgreSQL y pgAdmin 4

El proyecto utiliza PostgreSQL como motor de base de datos relacional. Sigue estos pasos para prepararla:

1. Abre pgAdmin 4 en tu equipo e inicia sesión.
2. Haz clic derecho sobre Databases -> Create -> Database...
3. En la ventana flotante, configura los siguientes campos:
   - Database: carniceria_db
   - Owner: postgres
4. Haz clic en Save para crearla.

> Nota: Si tienes un archivo .sql de respaldo, abre la "Query Tool" en la nueva base de datos y ejecuta tu script ahí antes de conectar Django.

---

## Paso 2: Clonar el Proyecto y Preparar el Entorno Virtual

1. Abre tu terminal y clona el repositorio:
   git clone <URL_DE_TU_REPOSITORIO>
   cd nombre-del-proyecto

2. Crea y activa el entorno virtual:
   - Windows:
     python -m venv venv
     .\venv\Scripts\activate
   - macOS/Linux:
     python3 -m venv venv
     source venv/bin/activate

---

## Paso 3: Instalar las Dependencias

Con el entorno virtual activo, ejecuta:
pip install django psycopg2-binary

---

## Paso 4: Configurar la Conexión

Edita el bloque DATABASES en tu archivo settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'carniceria_db',
        'USER': 'postgres',
        'PASSWORD': 'TU_CONTRASEÑA',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


---

## Paso 5: Ejecutar el Servidor

python manage.py runserver

Abre tu navegador en: http://127.0.0.1:8000/

---

## Módulos Operacionales

- /stock/: Control de inventario en tiempo real con algoritmo FEFO.
- /productos/: Catálogo maestro de SKUs.
- /stock/llegada/: Módulo de recepción de mercadería (utiliza sentencias SQL de tipo UPSERT).
