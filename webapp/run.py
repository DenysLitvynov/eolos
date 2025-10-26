"""
Autor: Denys Litvynov Lymanets
Fecha: 28-09-2025
Descripción: Ejecuta el servidor FastAPI desde la raíz.
"""

# ---------------------------------------------------------

import uvicorn

# ---------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",  
        host="127.0.0.1",
        port=8000,
        reload=True
    )

# ---------------------------------------------------------
