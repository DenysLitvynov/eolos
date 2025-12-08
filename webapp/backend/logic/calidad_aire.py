"""
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Lógica de negocio para obtener la calidad del aire (AQI).
"""

# ---------------------------------------------------------

from sqlalchemy.orm import Session
from ..db.models import Medida
from datetime import datetime

# ---------------------------------------------------------

class LogicaCalidadAire:

    def convertir_pm25_a_aqi(self, pm25_valor):
        """
        Convierte valor de PM2.5 (µg/m³) a AQI.
        Basado en el estándar EPA.
        
        Args:
            pm25_valor (float): Valor de PM2.5 en µg/m³
        
        Returns:
            int: Valor AQI
        """
        if pm25_valor <= 12.0:
            return int((pm25_valor / 12.0) * 50)
        elif pm25_valor <= 35.4:
            return int(50 + ((pm25_valor - 12.0) / (35.4 - 12.0)) * 50)
        elif pm25_valor <= 55.4:
            return int(100 + ((pm25_valor - 35.4) / (55.4 - 35.4)) * 50)
        elif pm25_valor <= 150.4:
            return int(150 + ((pm25_valor - 55.4) / (150.4 - 55.4)) * 50)
        else:
            return int(200 + ((pm25_valor - 150.4) / (250.4 - 150.4)) * 50)

    def obtener_aqi_reciente(self, db: Session, placa_id: str):
        """
        Obtiene el AQI más reciente de una placa específica.
        Calcula el AQI a partir de la medición PM2.5 más reciente.
        
        Args:
            db (Session): Sesión de BD.
            placa_id (str): ID de la placa.
        
        Returns:
            dict: {"aqi": int, "fecha_hora": str}
        """
        try:
            medicion = db.query(Medida).filter(
                Medida.placa_id == placa_id,
                Medida.tipo == "pm2_5"
            ).order_by(Medida.fecha_hora.desc()).first()
            
            if not medicion:
                raise ValueError(f"No hay mediciones PM2.5 para la placa {placa_id}")
            
            aqi = self.convertir_pm25_a_aqi(medicion.valor)
            
            return {
                "aqi": aqi,
                "fecha_hora": medicion.fecha_hora.isoformat()
            }
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error obteniendo AQI: {e}")

    def obtener_historico_24h(self, db: Session, placa_id: str):
        """
        Obtiene todas las mediciones de las últimas 24 horas para una placa.
        
        Args:
            db (Session): Sesión de BD.
            placa_id (str): ID de la placa.
        
        Returns:
            list: Lista de mediciones ordenadas por fecha
        """
        try:
            from datetime import datetime, timedelta, timezone
            hace_24h = datetime.now(timezone.utc) - timedelta(hours=24)
            
            mediciones = db.query(Medida).filter(
                Medida.placa_id == placa_id,
                Medida.fecha_hora >= hace_24h
            ).order_by(Medida.fecha_hora.asc()).all()
            
            if not mediciones:
                raise ValueError(f"No hay mediciones en las últimas 24 horas para {placa_id}")
            
            return [
                {
                    "valor": float(m.valor),
                    "fecha_hora": m.fecha_hora.isoformat(),
                    "aqi": self.convertir_pm25_a_aqi(m.valor)
                }
                for m in mediciones
            ]
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error obteniendo histórico: {e}")

# ---------------------------------------------------------