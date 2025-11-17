# Guía de Instalación y Configuración - Eolos WebApp

## 📋 Prerrequisitos

- Git instalado
- Python 3.7+
- PostgreSQL
- pip (gestor de paquetes de Python)

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio

```bash
git clone <enlace-de-github>
cd eolos/webapp
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la carpeta `webapp` con el siguiente contenido:

```env
# .env
SMTP_SERVER=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=
BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://postgres:1234@localhost:5432/pbio_eolos
JWT_SECRET=una_clave_muy_segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

## 🗄️ Instalación y Configuración de PostgreSQL

### Linux (Fedora/RHEL)

```bash
# Verificar si PostgreSQL está instalado
psql --version

# Si no está instalado, instalar:
sudo dnf install postgresql-server postgresql-contrib -y

# Inicializar la base de datos (solo primera vez)
sudo postgresql-setup --initdb

# Iniciar el servicio
sudo systemctl start postgresql

# Verificar estado
sudo systemctl status postgresql
```

### Windows

1. Descargar PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/windows/)
2. Ejecutar el instalador y seguir las instrucciones
3. Durante la instalación, establecer contraseña `1234` para el usuario postgres
4. Crear la base de datos `pbio_eolos` usando pgAdmin o línea de comandos

### macOS

```bash
# Instalar con Homebrew
brew install postgresql

# Iniciar servicio
brew services start postgresql

# O instalar desde postgresapp.com (GUI)
```

## 🔧 Configuración de la Base de Datos

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# En la consola de PostgreSQL, ejecutar:
ALTER USER postgres WITH PASSWORD '1234';
CREATE DATABASE pbio_eolos;
GRANT ALL PRIVILEGES ON DATABASE pbio_eolos TO postgres;

# Salir de psql
\q

# Probar conexión
psql -h localhost -U postgres -d pbio_eolos
# Contraseña: 1234

# Si entra correctamente, salir con:
\q
```

## 🐍 Entorno Virtual Python

### Crear y activar entorno virtual

```bash
# Desde la carpeta webapp
python3 -m venv venv
```

### Activación del entorno virtual

**Linux/macOS:**
```bash
# Bash
source venv/bin/activate

# Fish
source venv/bin/activate.fish

# Zsh
source venv/bin/activate
```

**Windows:**
```cmd
# Command Prompt
venv\Scripts\activate

# PowerShell
venv\Scripts\Activate.ps1
```

## 📦 Instalación de Dependencias

Con el entorno virtual activado:

```bash
# Actualizar pip
pip install --upgrade pip

# Opción 1: Instalar dependencias individualmente
pip install fastapi uvicorn sqlalchemy alembic python-dotenv passlib[bcrypt] psycopg2-binary pydantic[email] python-multipart pyjwt

# Opción 2: Si existe requirements.txt
pip install -r requirements.txt
```

## 🗃️ Migraciones de Base de Datos

```bash
# Verificar migraciones existentes
ls backend/migrations/versions

# Si no hay migraciones, generar la inicial
alembic revision --autogenerate -m "Inicial: Crea tablas de models"

# Aplicar migraciones
alembic upgrade head
```

## 🌱 Poblar Base de Datos (Seed)

```bash
# Navegar a la carpeta de la base de datos
cd backend/db

# Solucionar posibles conflictos con bcrypt
pip uninstall -y bcrypt
pip install bcrypt==4.1.2
pip install --force-reinstall passlib

# Ejecutar script de seed
python seed.py
```

**Nota:** Si aparece el error:
```
(trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```
No afecta el funcionamiento, siempre que luego muestre "Seed completado: ..."

Regresar a la carpeta principal:
```bash
cd ../..
```

## 🚀 Ejecutar el Servidor

Desde la carpeta `webapp`:

### Opción 1: Con run.py
```bash
python run.py
```

### Opción 2: Con uvicorn (recomendado para desarrollo)
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```
📱 Integración con Android

⚠️ IMPORTANTE: Si se integra con un cliente Android, es necesario:

    Ejecutar el servidor con acceso externo:
    bash

uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

Obtener la IP del servidor:

    Linux/macOS: hostname -I o ip addr show

    Windows: ipconfig

En el cliente Android, usar la IP del servidor en lugar de localhost:
text

http://[IP-DEL-SERVIDOR]:8000

Verificar firewall para permitir conexiones en el puerto 8000
## 🔍 Probar la Aplicación

- **Aplicación web:** http://localhost:8000/
- **Documentación API:** http://localhost:8000/docs (Swagger)

### 👤 Usuarios de Prueba

**Usuario normal:**
- Email: `pepe@fake.com`
- Contraseña: `Password123!`

**Usuario administrador:**
- Email: `admin@fake.com`
- Contraseña: `Admin123!`

## ❗ Solución de Problemas Comunes

### Error de conexión a PostgreSQL
- Verificar que el servicio esté ejecutándose
- Confirmar credenciales en el archivo `.env`
- Asegurar que la base de datos `pbio_eolos` existe

### Error de dependencias
- Verificar que el entorno virtual esté activado
- Ejecutar `pip install --upgrade pip` antes de instalar dependencias

### Error de migraciones
- Verificar que la base de datos esté creada y accesible
- Confirmar que los modelos estén correctamente definidos

## 📞 Soporte

Si encuentras problemas durante la instalación, verifica:
1. Todas las variables en `.env` son correctas
2. PostgreSQL está ejecutándose
3. El entorno virtual está activado
4. Todas las dependencias están instaladas
