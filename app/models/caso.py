from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class StatusCasoEnum(str, enum.Enum):
    pendente = "pendente"
    aceito = "aceito"
    recusado = "recusado"
    finalizado = "finalizado"

class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    status = Column(Enum(StatusCasoEnum), default=StatusCasoEnum.pendente)
    resumo = Column(String)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    advogado_id = Column(Integer, ForeignKey("advogados.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="casos")
    advogado = relationship("Advogado", back_populates="casos")
    mensagens = relationship("Mensagem", back_populates="caso")