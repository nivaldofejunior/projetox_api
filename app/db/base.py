from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Importa os modelos diretamente para garantir que as tabelas sejam registradas
from app.models.cliente import Cliente
from app.models.advogado import Advogado
from app.models.caso import Caso
from app.models.mensagem import Mensagem
