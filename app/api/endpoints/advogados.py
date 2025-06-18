from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.advogado import Advogado
from app.models.caso import Caso
from app.schemas.advogado import AdvogadoCreate, AdvogadoOut
from app.schemas.caso import CasoOut
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=AdvogadoOut, status_code=status.HTTP_201_CREATED)
def criar_advogado(advogado: AdvogadoCreate, db: Session = Depends(get_db)):
    db_advogado = db.query(Advogado).filter(Advogado.email == advogado.email).first()
    if db_advogado:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo_advogado = Advogado(
        nome=advogado.nome,
        email=advogado.email,
        senha_hash=advogado.senha
    )
    db.add(novo_advogado)
    db.commit()
    db.refresh(novo_advogado)
    return novo_advogado

@router.get("/{advogado_id}/casos", response_model=list[CasoOut])
def listar_casos_aceitos_por_advogado(advogado_id: int, db: Session = Depends(get_db)):
    advogado = db.query(Advogado).filter(Advogado.id == advogado_id).first()
    if not advogado:
        raise HTTPException(status_code=404, detail="Advogado não encontrado")
    return db.query(Caso).filter(Caso.advogado_id == advogado_id).all()

@router.get("/", response_model=list[AdvogadoOut])
def listar_advogados(db: Session = Depends(get_db)):
    return db.query(Advogado).all()
