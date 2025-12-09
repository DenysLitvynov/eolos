# 📘 Guía Completa (Docker-only) — Eolos WebApp

**Objetivo:** Esta guía está pensada para que cualquier persona, incluso sin experiencia previa, pueda clonar el repositorio, levantar toda la aplicación (frontend + backend + base de datos) con Docker, poblar la base de datos y empezar a trabajar sin romperse la cabeza.

Todo funciona con Docker + Docker Compose.
No necesitas instalar Python ni PostgreSQL en tu sistema. 

---

## 1️⃣ Requisitos previos (instalación de Docker)

* Docker Engine: [https://docs.docker.com/engine/](https://docs.docker.com/engine/)
* Docker Desktop (Windows / macOS): [https://docs.docker.com/desktop/](https://docs.docker.com/desktop/)

Comprueba que están instalados:

```bash
docker --version
docker compose version
```

---

## 2️⃣ Clonar el repositorio

```bash
git clone <URL-DEL-REPO>
cd eolos/webapp
```

---

## 3️⃣ Configurar `.env` (archivo obligatoria en `webapp/`)

Crea `webapp/.env` con este contenido (valores de ejemplo):

```env
DATABASE_URL=postgresql://postgres:123456@db:5432/pbio_eolos
JWT_SECRET=una_clave_muy_segura
BASE_URL=http://localhost

# Email (Brevo)
SMTP_SERVER=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=

ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

> **No subir** el `.env` con credenciales reales al repositorio.

---

## 4️⃣ Construir las imágenes Docker

Hazlo **una vez** o cuando cambies Dockerfiles / dependencias / frontend estático (ver sección “¿Cuándo reconstruir imágenes?”).

Desde `webapp/`:

```bash
docker compose build
```

— Para construir solo un servicio (p. ej. backend):

```bash
docker compose build backend
```

---

## 5️⃣ Levantar los contenedores (Linux / macOS / Windows)

Antes de arrancar, si tienes Postgres **instalado localmente** debes pararlo para evitar conflicto en el puerto 5432:

* **Linux (systemd)**:

  ```bash
  sudo systemctl stop postgresql
  ```
* **macOS (Homebrew)**:

  ```bash
  brew services stop postgresql
  ```
* **Windows** (PowerShell como administrador):

  ```powershell
  Stop-Service -Name postgresql*   # o usar services.msc y parar el servicio PostgreSQL
  ```

Ahora arranca la pila:

```bash
docker compose up -d
```

Si necesitas forzar rebuild y arrancar:

```bash
docker compose up -d --build
```

Comprobar contenedores:

```bash
docker compose ps
```

Debes ver: `db`, `backend`, `frontend` → estado `Up`.

---

## 6️⃣ Poblar la base de datos (seed)

Dentro de `webapp/`, elegir una de las dos opciones:

* Datos de prueba simples:

  ```bash
  docker compose exec backend python backend/db/seed.py
  ```
* Datos más realistas:

  ```bash
  docker compose exec backend python backend/db/seed_realistic.py
  ```

Si hay errores: ver logs del backend (más abajo).

---

## 7️⃣ Probar la aplicación (URLs)

* **Frontend (WebApp):** `http://localhost`
* **Docs / Swagger (API):** `http://localhost:8000/docs`
* **API base (FastAPI):** `http://localhost:8000/api/v1`

---

## 8️⃣ Integración con Android / clientes externos

1. Asegúrate que Backend está corriendo en `0.0.0.0` (ya lo hace en Docker).
2. Obtén la IP del equipo anfitrión:

* **Linux/macOS:** `hostname -I` o `ip addr show`
* **Windows:** `ipconfig`

3. En la app Android usa `http://<IP_DEL_PC>:8000` (no `localhost`).
4. Comprueba firewall / reglas de red para permitir el puerto 8000.

---

## 9️⃣ Logs y depuración (comandos)

* Logs de todos los servicios (en tiempo real):

  ```bash
  docker compose logs -f
  ```
* Logs solo backend:

  ```bash
  docker compose logs -f backend
  ```
* Ver estado rápido:

  ```bash
  docker compose ps
  ```

---

## 🔴 Parar todo (comando explícito)

* **Parar contenedores y eliminar redes/containers (mantiene volúmenes):**

  ```bash
  docker compose down
  ```

* **Parar y eliminar también volúmenes de datos (borra la BD):**

  ```bash
  docker compose down -v
  ```

* **Solo parar (no eliminar):**

  ```bash
  docker compose stop
  ```

Usa `down -v` con cuidado: borra la base de datos persistida.

---

## 🔁 ¿Cuándo y cómo reconstruir imágenes? (explicación clara)

**Regla general:**

* Si cambias **dependencias** (`requirements.txt`) o los **Dockerfile**, o los **ficheros que se copian durante la build** (por ejemplo el frontend estático que se copia dentro de la imagen nginx), **debes reconstruir la imagen**.
* Si cambias **código Python del backend** y el backend tiene el proyecto montado como volumen (`volumes: - .:/app`) y uvicorn está en modo `--reload`, los cambios se aplican **sin** reconstruir (se recargan automáticamente).
* Si cambias solo **assets del frontend** (HTML/CSS/JS) y el frontend **no** tiene volumen montado (la Dockerfile copia `frontend/`), **debes reconstruir** el frontend.

### Casos concretos y comandos

1. **He cambiado solo código Python del backend (lógica, routers, templates, etc.)**

   * Si el `backend` está montando el código con `.:/app` y Uvicorn usa `--reload` (modo dev), **NO hace falta rebuild**.
   * Si no se recarga automáticamente: reinicia el contenedor backend:

     ```bash
     docker compose restart backend
     ```

2. **He cambiado `requirements.txt` (nuevas dependencias)**

   * Reconstruir backend y arrancar:

     ```bash
     docker compose build backend
     docker compose up -d --no-deps backend
     ```
   * O todo junto:

     ```bash
     docker compose up -d --build
     ```

3. **He cambiado `Dockerfile.backend` o archivos que el Dockerfile copia (sin volumen)**

   * Reconstruir backend:

     ```bash
     docker compose build backend
     docker compose up -d --no-deps backend
     ```

---

4. **He cambiado el frontend (HTML/CSS/JS)**

* **Opción A — Producción (Docker)**
  Si el frontend se copia en la imagen (`Dockerfile.frontend`), debes **reconstruir y reiniciar solo el servicio del frontend**:

  ```bash
  docker compose build frontend
  docker compose up -d --no-deps frontend
  ```

  Esto se usa para probar los cambios dentro del contenedor Nginx, como se verán en producción.

* **Opción B — Desarrollo rápido (recomendado para programadores de frontend)**
  Para desarrollo, lo más cómodo es **no usar Docker**. Así los cambios se reflejan al instante y no necesitas reconstruir imágenes:

  ```bash
  cd frontend
  npm install
  npm run dev
  ```

  La aplicación se abrirá en:

  ```
  http://localhost:5173
  ```

  ⚠️ Notas importantes:

  * En este modo, los cambios se recargan automáticamente.
  * Docker se utiliza solo para probar la versión compilada en producción.
  * Alternativamente, si quieres usar Docker para desarrollo, puedes montar el directorio `frontend/` como volumen en `docker-compose.yml` para reflejar cambios sin rebuild (solo recomendado para dev).

---

5. **He cambiado `nginx.conf`**

   * Reconstruir frontend (pues la config se copia en la imagen):

     ```bash
     docker compose build frontend
     docker compose up -d --no-deps frontend
     ```

6. **Quiero forzar todo (reconstruir y reiniciar toda la pila)**

   ```bash
   docker compose up -d --build
   ```

7. **Actualizar imágenes base (por ejemplo nueva versión de postgres)**

   * Pull y rebuild:

     ```bash
     docker compose pull
     docker compose up -d --build
     ```

---

## 🔧 Troubleshooting rápido (problemas comunes)

* **Contenedores no suben / crash** → `docker compose logs backend` y `docker compose logs db`.
* **Puerto 5432 en uso** → detén el Postgres local (ver sección 5).
* **Seed da error** → `docker compose logs backend` y ejecutar el seed de nuevo.
* **Cambios no aparecen** → si fue cambio en frontend, reconstruye la imagen; si fue backend y no tienes `--reload`, reinicia el contenedor.

---

## ✅ Usuarios de prueba (si los seeds los generan)

* **Usuario normal:** `pepe@fake.com` / `Password123!`
* **Administrador:** `admin@fake.com` / `Admin123!`

---

