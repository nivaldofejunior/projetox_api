from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.mensagem import Mensagem, TipoMensagemEnum, OrigemMensagemEnum
from app.models.caso import Caso
from app.schemas.mensagem import MensagemCreate, MensagemResponse
from app.db.session import get_db
from app.services.transcricao_service import transcrever_audio_local, transcrever_audio_da_url
import os, tempfile, re, unicodedata

router = APIRouter()

@router.post("/", response_model=MensagemResponse)
def criar_mensagem(mensagem_in: MensagemCreate, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter_by(id=mensagem_in.caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")

    nova_mensagem = Mensagem(**mensagem_in.model_dump())
    db.add(nova_mensagem)
    db.commit()
    db.refresh(nova_mensagem)

    if nova_mensagem.tipo == TipoMensagemEnum.audio and nova_mensagem.url_audio:
        transcricao = transcrever_audio_da_url(nova_mensagem.url_audio)
        nova_mensagem.transcricao = transcricao
        db.commit()
        db.refresh(nova_mensagem)

    return nova_mensagem

@router.post("/upload", response_model=MensagemResponse)
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
    nome_final = f"{nome_base}.ogg"

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

@router.get("/caso/{caso_id}", response_model=list[MensagemResponse])
def listar_mensagens_do_caso(caso_id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    return caso.mensagens

def limpar_nome_arquivo(nome: str) -> str:
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    nome = re.sub(r'\s+', '_', nome)
    nome = re.sub(r'[^\w.-]', '', nome)
    return nome

@router.get("/audios", response_model=list[MensagemResponse])
def listar_audios(db: Session = Depends(get_db)):
    return db.query(Mensagem).filter(Mensagem.tipo == TipoMensagemEnum.audio).all()
