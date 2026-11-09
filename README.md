# MUC · Museo Universitario de la Cultura (UCSE)

Sitio web del museo: portada con fotos, presentaciones (exposiciones, muestras, charlas, talleres),
galería de obras, recorrido virtual en 3D/realidad virtual (A-Frame), opciones de accesibilidad
y panel de estadísticas de uso.

El repositorio **ya incluye la base de datos y las imágenes** con los datos de la demo
(obras, presentaciones y estadísticas de ejemplo), así que no hace falta cargar nada.

## Requisitos

- Python 3.10 o superior: https://www.python.org/downloads/
  (en Windows, al instalar, tildar **"Add Python to PATH"**).
- En Mac, el `python3` que viene con el sistema suele ser 3.9 y **no sirve**: instalar uno nuevo desde python.org
  y verificar con `python3 --version`.

## Cómo abrirlo

### Windows (PowerShell o CMD, dentro de la carpeta del proyecto)

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python manage.py migrate
venv\Scripts\python manage.py runserver 8002
```

### Mac / Linux

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py migrate
venv/bin/python manage.py runserver 8002
```

Después abrir en el navegador: **http://localhost:8002**

Los tres primeros comandos se hacen una sola vez. Las siguientes veces alcanza con el último
(`runserver`).

## Accesos

- Sitio: http://localhost:8002
- Recorrido virtual: http://localhost:8002/obras/sala-virtual/
- Panel de administración: http://localhost:8002/admin/ (usuario `admin`, contraseña `admin12345`)
- Estadísticas: http://localhost:8002/admin/estadisticas/ (o el botón «📊 Estadísticas del sitio» en el admin)

## Abrirlo desde el celular

Con la compu y el celular en el mismo wifi, iniciar el servidor así:

```
python manage.py runserver 0.0.0.0:8002
```

y en el celular entrar a `http://IP-DE-LA-COMPU:8002`
(la IP se ve con `ipconfig` en Windows o `ipconfig getifaddr en0` en Mac).

## Estadísticas de demostración

Las estadísticas de ejemplo cubren los 45 días anteriores a cuando se generaron. Para que lleguen
hasta el día de hoy, regenerarlas con:

```
python manage.py seed_analitica --dias 45
```

(usar `venv\Scripts\python` o `venv/bin/python` según el sistema). Para borrarlas y ver solo
visitas reales: `python manage.py seed_analitica --borrar`.

## Cargar contenido

Todo se administra desde `/admin/`:

- **Fotos de portada**: las fotos del museo que rotan en la pantalla principal.
- **Presentaciones**: se separan solas en "en cartel y próximas" y "anteriores" según las fechas.
- **Obras**: aparecen en la galería y, si tienen tildado "mostrar en la sala virtual", se cuelgan
  automáticamente en las paredes de la sala 3D (hasta 13), respetando la proporción de cada imagen.

Los títulos, autores y descripciones de las obras y presentaciones son **datos ficticios de ejemplo**
para la demostración del prototipo.
