from time import monotonic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from gemini_service import MODELO, gerar_resposta

app = FastAPI()

TTL_SEGUNDOS = 30

cache = {}

class SolicitacaoPrompt(BaseModel):
    idade: int = Field(ge=0, le=120) 
    pergunta: str = Field(min_length=3, max_length=300)

@app.get("/")
def inicio():
    return {
        "mensagem": "Microserviço com Gemini funcionando!"
    }

@app.post("/prompts")
def criar_prompts(dados: SolicitacaoPrompt):
    if dados.idade < 18:
        raise HTTPException(
            status_code=403,
            detail="Serviço destinado para pessoas com 18 anos ou mais."
        )
    
    pergunta = dados.pergunta.strip()

    chave =(MODELO, pergunta)

    agora = monotonic()

    registro = cache.get(chave)

    if registro and agora < registro["expira_em"]:
        return {
            "resposta": registro["resposta"],
            "cache": "HIT",
            "ttl_restante_segundos": round(
                registro["expira_em"] - agora, 1
            )
        }
    if registro:
        del cache[chave]
    
    try:
        resposta = gerar_resposta(pergunta)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível obter uma resposta do Gemini",
        )
    
    cache[chave] = {
        "resposta": resposta,
        "expira_em": monotonic() + TTL_SEGUNDOS
    }

    return {
        "resposta": resposta,
        "cache": "MISS",
        "ttl_segundos": TTL_SEGUNDOS,
    }

@app.delete("/cache")
def limpar_cache():
    cache.clear()
    return {"mensagem": "Cache limpo com sucesso."}