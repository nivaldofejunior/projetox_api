from pydantic import BaseModel
from datetime import datetime

class AdvogadoCreate(BaseModel):
    nome: str
    email: str
    senha: str

class AdvogadoOut(BaseModel):
    id: int
    nome: str
    email: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
