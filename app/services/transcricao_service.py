import os
from groq import Groq
from tempfile import NamedTemporaryFile
import requests

def transcrever_audio_da_url(url: str) -> str:
    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Erro ao baixar o áudio: {response.status_code}")

        with NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio:
            for chunk in response.iter_content(chunk_size=8192):
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        return transcrever_audio_local(temp_audio_path)

    except Exception as e:
        return f"[Erro na transcrição: {str(e)}]"


def transcrever_audio_local(caminho: str) -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with open(caminho, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(caminho), file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
            )
            return transcription.text
    except Exception as e:
        return f"[Erro na transcrição local: {str(e)}]"
