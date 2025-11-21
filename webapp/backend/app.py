"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Archivo principal de la aplicación FastAPI.
Crea la app FastAPI, genera las tablas si no existen, monta las rutas, maneja los CORS y sirve el frontend de la aplicación web.
"""

# ---------------------------------------------------------

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .api.auth import router as auth_router  # Agregado para auth
from .db.database import engine
from .db.models import Base

from .api import incidencias_api
from .api import perfil_api
from .api import trayectos_api
from .api import calidad_aire_api
from .api import estado_sensores_api

# ---------------------------------------------------------

app = FastAPI(title="API REST para Proyecto Biometría y Medio Ambiente", version="1.0.0")

# Crear tablas si no existen 
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(perfil_api.router, prefix="/api/v1")
app.include_router(incidencias_api.router, prefix="/api/v1")
app.include_router(trayectos_api.router, prefix="/api/v1")  
app.include_router(calidad_aire_api.router, prefix="/api/v1")
app.include_router(estado_sensores_api.router, prefix="/api/v1")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos estáticos
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

#app.mount("/logica_fake", StaticFiles(directory=FRONTEND_DIR / "logica_fake"), name="logica_fake")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
#app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR / "frontend"), name="frontend")
app.mount("/images", StaticFiles(directory=FRONTEND_DIR / "images"), name="images")
app.mount("/pages", StaticFiles(directory=FRONTEND_DIR / "pages"), name="pages")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")

@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "index.html")
# ---------------------------------------------------------

