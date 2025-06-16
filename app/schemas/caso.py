from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.caso import StatusCasoEnum
from app.schemas.mensagem import MensagemResponse

class CasoCreate(BaseModel):
    titulo: str
    cliente_id: int

class CasoUpdate(BaseModel):
    titulo: Optional[str]
    status: Optional[StatusCasoEnum]
    resumo: Optional[str]
    advogado_id: Optional[int]

class CasoOut(BaseModel):
    id: int
    titulo: str
    status: StatusCasoEnum
    resumo: Optional[str]
    cliente_id: int
    advogado_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    mensagens: List[MensagemResponse] = []

    model_config = {
        "from_attributes": True
    }