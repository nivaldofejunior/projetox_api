from sqlalchemy.orm import declarative_base
from fastapi import APIRouter

Base = declarative_base()

# Importa os modelos para registrar no metadata
def import_models():
    from app.models.cliente import Cliente
    from app.models.advogado import Advogado
    from app.models.caso import Caso
    from app.models.mensagem import Mensagem

router = APIRouter()

