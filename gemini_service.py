import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

MODELO = "gemini-3.5-flash-lite"

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "Configure a variável de ambiente GEMINI_API_KEY."
    )

client = genai.Client(api_key=api_key)


def gerar_resposta(pergunta: str) -> str:

    resposta = client.models.generate_content(
        model=MODELO,
        contents=pergunta,
        config={
            "system_instruction": (
                "Você é um assistente didático. "
                "Responda com clareza e exemplos simples."
            ),
            "temperature": 0.3,
            "max_output_tokens": 500,
        },
    )

    if not resposta.text:
        raise RuntimeError("O Gemini não retornou texto.")

    return resposta.text