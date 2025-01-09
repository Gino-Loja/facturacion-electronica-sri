from pydantic import BaseModel
from datetime import date

class Digital_certificate(BaseModel):
    certificado: str   # Datos binarios (bytea en PostgreSQL)
    password: str       # Texto plano
    fecha_caducidad: date  # Fecha específica