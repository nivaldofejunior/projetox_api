from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class TipoMensagemEnum(str, enum.Enum):
    texto = "texto"
    audio = "audio"

class OrigemMensagemEnum(str, enum.Enum):
    cliente = "cliente"
    ia = "ia"
    advogado = "advogado"

class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoMensagemEnum), nullable=False)
    conteudo_texto = Column(String, nullable=True)
    url_audio = Column(String, nullable=True)
    transcricao = Column(String, nullable=True)
    origem = Column(Enum(OrigemMensagemEnum), nullable=False)
    caso_id = Column(Integer, ForeignKey("casos.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    caso = relationship("Caso", back_populates="mensagens")