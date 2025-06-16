from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.cliente import ClienteCreate, ClienteOut
from app.schemas.caso import CasoCreate, CasoOut
from app.schemas.mensagem import MensagemCreate, MensagemResponse
from app.schemas.advogado import AdvogadoCreate, AdvogadoOut
from app.models.cliente import Cliente
from app.models.caso import Caso, StatusCasoEnum
from app.models.mensagem import Mensagem, TipoMensagemEnum, OrigemMensagemEnum
from app.models.advogado import Advogado
from app.db.session import get_db
from app.services.ia_service import gerar_resumo_do_caso
from app.services.transcricao_service import transcrever_audio_da_url, transcrever_audio_local
from groq import Groq
import tempfile
import os
import re
import unicodedata

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Projeto X API funcionando"}

@router.post("/clientes/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = db.query(Cliente).filter(Cliente.cpf == cliente.cpf).first()
    if db_cliente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    novo_cliente = Cliente(**cliente.dict())
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente

@router.post("/casos/", response_model=CasoOut, status_code=status.HTTP_201_CREATED)
def criar_caso(caso: CasoCreate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == caso.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    novo_caso = Caso(titulo=caso.titulo, cliente_id=caso.cliente_id)
    db.add(novo_caso)
    db.commit()
    db.refresh(novo_caso)
    return novo_caso

@router.get("/casos/pendentes", response_model=list[CasoOut])
def listar_casos_pendentes(db: Session = Depends(get_db)):
    casos = db.query(Caso).filter(Caso.status == StatusCasoEnum.pendente).all()
    return casos

@router.get("/advogados/{advogado_id}/casos", response_model=list[CasoOut])
def listar_casos_aceitos_por_advogado(advogado_id: int, db: Session = Depends(get_db)):
    advogado = db.query(Advogado).filter(Advogado.id == advogado_id).first()
    if not advogado:
        raise HTTPException(status_code=404, detail="Advogado não encontrado")
    casos = db.query(Caso).filter(Caso.advogado_id == advogado_id).all()
    return casos

@router.get("/casos/{caso_id}/mensagens", response_model=list[MensagemResponse])
def listar_mensagens_do_caso(caso_id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    return caso.mensagens

@router.post("/mensagens/upload", response_model=MensagemResponse)
def upload_mensagem_audio(
    file: UploadFile = File(...),
    caso_id: int = Form(...),
    db: Session = Depends(get_db)
):
    caso = db.query(Caso).filter_by(id=caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")

    nome_original = limpar_nome_arquivo(file.filename)
    nome_base, _ = os.path.splitext(nome_original)
    extensao_corrigida = ".ogg"  # pode ajustar para .m4a ou .wav se necessário
    nome_final = f"{nome_base}{extensao_corrigida}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=nome_final) as temp:
        temp.write(file.file.read())
        temp_path = temp.name

    try:
        transcricao = transcrever_audio_local(temp_path)
    finally:
        os.remove(temp_path)

    nova_mensagem = Mensagem(
        tipo=TipoMensagemEnum.audio,
        origem=OrigemMensagemEnum.cliente,
        url_audio=None,
        transcricao=transcricao,
        caso_id=caso_id
    )
    db.add(nova_mensagem)
    db.commit()
    db.refresh(nova_mensagem)

    return nova_mensagem


@router.post("/mensagens/", response_model=MensagemResponse)
def criar_mensagem(mensagem_in: MensagemCreate, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter_by(id=mensagem_in.caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")

    nova_mensagem = Mensagem(**mensagem_in.model_dump())
    nova_mensagem.caso = caso
    db.add(nova_mensagem)
    db.commit()
    db.refresh(nova_mensagem)

    if nova_mensagem.tipo == TipoMensagemEnum.audio and nova_mensagem.url_audio:
        transcricao = transcrever_audio_da_url(nova_mensagem.url_audio)
        nova_mensagem.transcricao = transcricao
        db.commit()
        db.refresh(nova_mensagem)

    return nova_mensagem

@router.post("/casos/{id}/resumir", response_model=CasoOut)
def resumir_caso(id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    resumo = gerar_resumo_do_caso(caso)
    caso.resumo = resumo
    db.commit()
    db.refresh(caso)
    return caso

@router.patch("/casos/{id}", response_model=CasoOut)
def atualizar_caso(id: int, caso_update: dict, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    for field, value in caso_update.items():
        setattr(caso, field, value)
    db.commit()
    db.refresh(caso)
    return caso

@router.post("/advogados/", response_model=AdvogadoOut, status_code=status.HTTP_201_CREATED)
def criar_advogado(advogado: AdvogadoCreate, db: Session = Depends(get_db)):
    db_advogado = db.query(Advogado).filter(Advogado.email == advogado.email).first()
    if db_advogado:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo_advogado = Advogado(
        nome=advogado.nome,
        email=advogado.email,
        senha_hash=advogado.senha  # ⚠️ hash real a ser implementado depois
    )
    db.add(novo_advogado)
    db.commit()
    db.refresh(novo_advogado)
    return novo_advogado

@router.post("/casos/{id}/aceitar", response_model=CasoOut)
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

def limpar_nome_arquivo(nome: str) -> str:
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    nome = re.sub(r'\s+', '_', nome)  # espaços por _
    nome = re.sub(r'[^\w.-]', '', nome)  # remove tudo que não for letra, número, _ . ou -
    return nome