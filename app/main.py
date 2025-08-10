
import os, sys; print("CWD:", os.getcwd()); print("PYTHONPATH:", sys.path[:3])
import logging
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.database import engine, Base, get_db
from app import models

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app")
print("BOOT: cargo app/main.py")           # debe salir al arrancar
logger.debug("BOOT: logger inicializado")

"""from .models import Cliente  
"""
load_dotenv()

# Crear tablas si no existen (dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mi App CRUD (FastAPI + PostgreSQL)")

# Static
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Jinja2
templates = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=select_autoescape(["html", "xml"]),
)

def render(template_name: str, **context):
    template = templates.get_template(template_name)
    return HTMLResponse(template.render(**context))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render("home.html", title="Inicio")

# CRUD Productos

@app.get("/productos", response_class=HTMLResponse)
def listar_productos(request: Request, db: Session = Depends(get_db)):
    print("DEBUG: Entrando en /productos")  # <- para saber que la función se ejecuta
    productos = db.execute(select(models.Producto).order_by(models.Producto.id.desc())).scalars().all()
    return render("productos_list.html", title="Productos", productos=productos)

@app.get("/productos/nuevo", response_class=HTMLResponse)
def nuevo_producto_form(request: Request):
    return render("producto_form.html", title="Nuevo Producto", producto=None, action="/productos/crear")

@app.post("/productos/crear")
def crear_producto(
    nombre: str = Form(...),
    descripcion: str = Form(None),
    precio: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db),
):
    producto = models.Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock)
    db.add(producto)
    db.commit()
    return RedirectResponse(url="/productos", status_code=303)

@app.get("/productos/{producto_id}", response_class=HTMLResponse)
def detalle_producto(request: Request, producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(models.Producto, producto_id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    return render("producto_detalle.html", title=f"Producto #{producto_id}", producto=producto)

@app.get("/productos/{producto_id}/editar", response_class=HTMLResponse)
def editar_producto_form(request: Request, producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(models.Producto, producto_id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    return render("producto_form.html", title=f"Editar Producto #{producto_id}", producto=producto, action=f"/productos/{producto_id}/actualizar")

@app.post("/productos/{producto_id}/actualizar")
def actualizar_producto(
    producto_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(None),
    precio: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db),
):
    producto = db.get(models.Producto, producto_id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    producto.nombre = nombre
    producto.descripcion = descripcion
    producto.precio = precio
    producto.stock = stock
    db.commit()
    return RedirectResponse(url=f"/productos/{producto_id}", status_code=303)

@app.post("/productos/{producto_id}/eliminar")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(models.Producto, producto_id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    db.delete(producto)
    db.commit()
    return RedirectResponse(url="/productos", status_code=303)

# --- CRUD Clientes ---

@app.get("/clientes", response_class=HTMLResponse)
def listar_clientes(request: Request, db: Session = Depends(get_db)):
    print("DEBUG: Entrando en /clientes")  # <- para saber que la función se ejecuta
    try:
        clientes = db.execute(select(models.Cliente).order_by(models.Cliente.id.desc())).scalars().all()
        logger.debug("DEBUG: %d clientes encontrados", len(clientes))
        print(f"DEBUG: {len(clientes)} clientes encontrados")  # <- cuántos registros hay
    except Exception:
        logger.exception("ERROR en la consulta a la base de datos")
        print("ERROR al consultar la base de datos")
        raise

    try:
        return render("clientes_list.html", title="Clientes", clientes=clientes)
    except Exception as e:
        print("ERROR al renderizar la plantilla:", e)
        raise

@app.get("/clientes/nuevo", response_class=HTMLResponse)
def nuevo_cliente_form(request: Request):
    return render("cliente_form.html", title="Nuevo Cliente", cliente=None, action="/clientes/crear")

@app.post("/clientes/crear")
def crear_cliente(
    nombre: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    db: Session = Depends(get_db),
):
    c = models.Cliente(nombre=nombre, email=email, telefono=telefono)
    db.add(c)
    db.commit()
    return RedirectResponse(url="/clientes", status_code=303)

@app.get("/clientes/{cliente_id}", response_class=HTMLResponse)
def detalle_cliente(request: Request, cliente_id: int, db: Session = Depends(get_db)):
    c = db.get(models.Cliente, cliente_id)
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    return render("cliente_detalle.html", title=f"Cliente #{cliente_id}", cliente=c)

@app.get("/clientes/{cliente_id}/editar", response_class=HTMLResponse)
def editar_cliente_form(request: Request, cliente_id: int, db: Session = Depends(get_db)):
    c = db.get(models.Cliente, cliente_id)
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    return render("cliente_form.html", title=f"Editar Cliente #{cliente_id}", cliente=c, action=f"/clientes/{cliente_id}/actualizar")

@app.post("/clientes/{cliente_id}/actualizar")
def actualizar_cliente(
    cliente_id: int,
    nombre: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    db: Session = Depends(get_db),
):
    c = db.get(models.Cliente, cliente_id)
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    c.nombre = nombre
    c.email = email
    c.telefono = telefono
    db.commit()
    return RedirectResponse(url=f"/clientes/{cliente_id}", status_code=303)

@app.post("/clientes/{cliente_id}/eliminar")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    c = db.get(models.Cliente, cliente_id)
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    db.delete(c)
    db.commit()
    return RedirectResponse(url="/clientes", status_code=303)

