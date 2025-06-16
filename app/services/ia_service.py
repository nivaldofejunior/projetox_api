import requests
from app.models.caso import Caso
from app.models.mensagem import Mensagem
from app.core.config import settings


def gerar_resumo_do_caso(caso: Caso) -> str:
    mensagens = caso.mensagens
    if not mensagens:
        return "Nenhuma mensagem disponível para resumir."

    partes = []
    for msg in mensagens:
        autor = msg.origem.upper()
        conteudo = msg.transcricao if msg.transcricao else msg.conteudo_texto
        if conteudo:
            partes.append(f"[{autor}]: {conteudo}")

    prompt = "\n".join(partes)

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "Você é um assistente jurídico que resume informações de casos recebidos de clientes."},
                    {"role": "user", "content": f"Resumo do caso:\n{prompt}"}
                ]
            },
            timeout=30
        )

        response.raise_for_status()
        resumo = response.json()["choices"][0]["message"]["content"]
        return resumo
    except Exception as e:
        return f"Erro ao gerar resumo com a IA: {str(e)}"