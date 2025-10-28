# Proyecto Aplicaciones Biometría Medioambiente EQ2


## Instalación paso a paso

### 1. Clonar el repositorio

```bash
cd ~/Projects  # O cd %USERPROFILE%\Projects en Windows
git clone https://github.com/DenysLitvynov/proyecto-aplicaciones-biometria-medioambiente-eq2.git
cd proyecto-aplicaciones-biometria-medioambiente-eq2
```

---

### 2. Crear entorno virtual

- **Linux/macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- **Windows:**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

Usa `deactivate` para salir del entorno virtual.

---

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Instalar PostgreSQL

Instala PostgreSQL 16+ según tu sistema operativo.

- **Linux (Fedora):**
  ```bash
  sudo dnf install postgresql-server postgresql-contrib -y
  sudo postgresql-setup --initdb
  sudo systemctl enable --now postgresql
  ```

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update
  sudo apt install postgresql postgresql-contrib -y
  sudo systemctl enable --now postgresql
  ```

- **macOS (Homebrew):**
  ```bash
  brew install postgresql@16
  brew services start postgresql@16
  ```

- **Windows:**
  1. Descarga el instalador desde [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
  2. Ejecuta como administrador y establece contraseña `123456` para usuario `postgres`.

---

### 5. Crear base de datos y usuario

```sql
CREATE DATABASE pbio_eolos;
CREATE USER postgres WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE pbio_eolos TO postgres;
\q
```

---

### 6. Configurar `.env`

Crea un archivo `.env` en la raíz del proyecto o en `webapp/backend`:

```env
DATABASE_URL=postgresql://postgres:123456@localhost:5432/pbio_eolos
JWT_SECRET=clave_secreta_equipo2_pl1
```

---

### 7. Limpiar base de datos (opcional)

Si quieres reiniciar la base antes de ejecutar seeds:

```bash
psql pbio_eolos -c "TRUNCATE TABLE usuarios, roles, mibisivalencia RESTART IDENTITY CASCADE;"
```

---

### 8. Ejecutar seeds (insertar datos de prueba)

```bash
python -m webapp.backend.db.seed
``` Esto crea tablas y datos iniciales.
---

### 9. Ejecutar la aplicación FastAPI

```bash
cd webapp
python run.py
```

O en modo desarrollo con recarga automática:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

API disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 10. Nota sobre Android

Si se integra con un cliente Android, es necesario indicar la **IP del dispositivo** donde se ejecuta el servidor para enviar las peticiones correctamente, en lugar de usar `localhost`.

---

## Notas finales

- Siempre activa el entorno virtual antes de usar Python.
- Para reiniciar completamente la base de datos:
  ```sql
  DROP SCHEMA public CASCADE;
  CREATE SCHEMA public;
  \q
  ```
  Luego ejecuta seeds nuevamente.
- Documentación API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

