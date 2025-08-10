# Plantilla FastAPI + PostgreSQL (CRUD completo)

Esta plantilla te da todas las pantallas para crear, insertar, consultar, editar y eliminar registros (CRUD) de un ejemplo `Producto`.

## Local (Windows + VS2022)

```bash
python -m venv .venv
.\.venv\Scriptsctivate
pip install -r requirements.txt
```

Crea la BD local y usuario:
```sql
CREATE DATABASE miapp;
CREATE USER miusuario WITH PASSWORD 'mipass';
GRANT ALL PRIVILEGES ON DATABASE miapp TO miusuario;
```

Copia `.env.example` a `.env` y ajusta:
```
DATABASE_URL=postgresql+psycopg2://miusuario:mipass@localhost:5432/miapp
```

Ejecuta:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Estructura
```
app/
  main.py
  database.py
  models.py
  templates/
    base.html
    home.html
    productos_list.html
    producto_form.html
    producto_detalle.html
  static/
    styles.css
```

## Despliegue (Ubuntu + Nginx + systemd)
- Crear venv, instalar requirements, configurar `.env`
- Probar con Uvicorn
- Servicio systemd con Gunicorn
- Nginx como reverse proxy (y alias para /static/)
