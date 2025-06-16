from app.core.config import settings
from app.db.base import Base, import_models
from app.db.session import engine

def init():
    print(f"🔗 Usando conexão: {settings.DB_URL}")
    print("⏳ Criando tabelas no banco...")

    import_models()  # ← GARANTE QUE OS MODELOS SÃO REGISTRADOS
    Base.metadata.create_all(bind=engine)

    print("✅ Tabelas criadas com sucesso.")

if __name__ == "__main__":
    init()
