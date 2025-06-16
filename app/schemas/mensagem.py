from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.mensagem import TipoMensagemEnum, OrigemMensagemEnum

class MensagemCreate(BaseModel):
    tipo: TipoMensagemEnum
    conteudo_texto: Optional[str]
    url_audio: Optional[str]
    origem: OrigemMensagemEnum
    caso_id: int

class MensagemResponse(BaseModel):
    id: int
    tipo: TipoMensagemEnum
    conteudo_texto: Optional[str]
    url_audio: Optional[str]
    transcricao: Optional[str]
    origem: OrigemMensagemEnum
    caso_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }