from fastapi import APIRouter
from app.api.endpoints import root, clientes, casos, mensagens, advogados

router = APIRouter()
router.include_router(root.router)
router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
router.include_router(casos.router, prefix="/casos", tags=["Casos"])
router.include_router(mensagens.router, prefix="/mensagens", tags=["Mensagens"])
router.include_router(advogados.router, prefix="/advogados", tags=["Advogados"])
