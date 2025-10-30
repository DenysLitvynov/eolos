"""
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Configuración de Alembic para migraciones de la base de datos.
"""

# ---------------------------------------------------------

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from pathlib import Path
import os
from backend.db.models import Base  # Vincular modelos

# Cargar .env desde la raíz del proyecto (webapp/)
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

# Depuración: Imprimir DATABASE_URL
print(f"DEBUG: DATABASE_URL = {os.getenv('DATABASE_URL')}")

# Interpretar el archivo de configuración para logging
config = context.config

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData para autogenerate
target_metadata = Base.metadata

def run_migrations_offline():
    """
    Ejecutar migraciones en modo offline.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    Ejecutar migraciones en modo online.
    """
    config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# ---------------------------------------------------------
