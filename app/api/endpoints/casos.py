from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.caso import Caso, StatusCasoEnum
from app.models.advogado import Advogado
from app.schemas.caso import CasoCreate, CasoOut
from app.db.session import get_db
from app.services.ia_service import gerar_resumo_do_caso

router = APIRouter()

@router.post("/", response_model=CasoOut)
def criar_caso(caso: CasoCreate, db: Session = Depends(get_db)):
    cliente = db.query(Caso.cliente.property.mapper.class_).get(caso.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    novo_caso = Caso(titulo=caso.titulo, cliente_id=caso.cliente_id)
    db.add(novo_caso)
    db.commit()
    db.refresh(novo_caso)
    return novo_caso

@router.get("/pendentes", response_model=list[CasoOut])
def listar_casos_pendentes(db: Session = Depends(get_db)):
    return db.query(Caso).filter(Caso.status == StatusCasoEnum.pendente).all()

@router.post("/{id}/resumir", response_model=CasoOut)
def resumir_caso(id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    resumo = gerar_resumo_do_caso(caso)
    caso.resumo = resumo
    db.commit()
    db.refresh(caso)
    return caso

@router.patch("/{id}", response_model=CasoOut)
def atualizar_caso(id: int, caso_update: dict, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    for field, value in caso_update.items():
        setattr(caso, field, value)
    db.commit()
    db.refresh(caso)
    return caso

@router.post("/{id}/aceitar", response_model=CasoOut)
def aceitar_caso(id: int, advogado_id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    if caso.status != StatusCasoEnum.pendente:
        raise HTTPException(status_code=400, detail="Caso já foi atribuído")
    advogado = db.query(Advogado).filter(Advogado.id == advogado_id).first()
    if not advogado:
        raise HTTPException(status_code=404, detail="Advogado não encontrado")
    caso.status = StatusCasoEnum.aceito
    caso.advogado_id = advogado.id
    db.commit()
    db.refresh(caso)
    return caso


@router.get("/", response_model=list[CasoOut])
def listar_todos_os_casos(db: Session = Depends(get_db)):
    return db.query(Caso).all()
