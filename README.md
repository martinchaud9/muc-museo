# MUC · Museo Universitario de la Cultura (UCSE)

Sitio web del museo: portada con fotos, presentaciones (exposiciones, muestras, charlas, talleres),
galería de obras y recorrido virtual en 3D/realidad virtual (A-Frame).

## Instalación

```bash
python3.12 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py migrate
venv/bin/python manage.py seed_demo      # admin/admin12345 + datos de ejemplo
venv/bin/python manage.py runserver 8002
```

## Cargar contenido

Todo se administra desde `/admin/`:

- **Fotos de portada**: las fotos del museo que rotan en la pantalla principal (si no hay ninguna, se ve un fondo provisorio).
- **Presentaciones**: se separan solas en "en cartel y próximas" y "anteriores" según las fechas.
- **Obras**: aparecen en la galería y, si tienen tildado "mostrar en la sala virtual", se cuelgan
  automáticamente en las paredes de la sala 3D (hasta 13), respetando la proporción de cada imagen.
