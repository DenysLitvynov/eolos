"""
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Archivo principal de la aplicación FastAPI. Configuramos app, middleware, rutas.
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

# ---------------------------------------------------------

app = FastAPI(title="API REST para Proyecto Biometría y Medio Ambiente", version="1.0.0")

# Crear tablas si no existen 
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth_router, prefix="/api/v1")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
