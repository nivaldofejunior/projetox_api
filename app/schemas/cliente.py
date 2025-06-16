from pydantic import BaseModel
from datetime import datetime

class ClienteCreate(BaseModel):
    nome: str
    cpf: str

class ClienteOut(BaseModel):
    id: int
    nome: str
    cpf: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }