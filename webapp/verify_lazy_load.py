from datetime import datetime, timezone
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, ".") # Run from project root

from backend.db.database import SessionLocal, engine, Base
from backend.db.models import CalidadGeneral
from backend.logic.mapas import LogicaMapas
from backend.pojos.posicion_gps import PosicionGPS

def verify():
    db = SessionLocal()
    try:
        # 1. Clear CalidadGeneral
        print("Limpiando tabla CalidadGeneral...")
        db.query(CalidadGeneral).delete()
        db.commit()
        
        count_before = db.query(CalidadGeneral).count()
        print(f"Count antes: {count_before}")
        assert count_before == 0
        
        # 2. Trigger Lazy Load
        print("Solicitando mapa general (trigger)...")
        logic = LogicaMapas()
        hoy = datetime.now(timezone.utc)
        inf_izq = PosicionGPS(38.9000, -0.2500)
        sup_der = PosicionGPS(39.1000, -0.1000)
        
        # This call should now trigger the calculation internally
        response = logic.obtener_mapa_de_tipo_de_dia_de_destino(db, "general", hoy, inf_izq, sup_der)
        
        # 3. Verify Response and DB
        data_points = 0
        for h, points in response["data"].items():
            data_points += len(points)
        
        print(f"Puntos devueltos en respuesta: {data_points}")
        
        count_after = db.query(CalidadGeneral).count()
        print(f"Count despues en DB: {count_after}")
        
        if count_after > 0:
            print("SUCCESS: Datos calculados y guardados bajo demanda.")
        else:
            print("FAILURE: No se guardaron datos.")
            return

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify()
