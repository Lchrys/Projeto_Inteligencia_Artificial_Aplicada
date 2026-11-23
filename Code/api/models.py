"""Modelos Pydantic de entrada e saída da API."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SaudeOut(BaseModel):
    status: str
    servico: str


class PontoSerie(BaseModel):
    model_config = ConfigDict(extra="allow")
    ano: float | int
    valor: float


class SerieOut(BaseModel):
    fonte: str
    codigo_serie: str
    data_extracao: str
    inicio: int | None = None
    fim: int | None = None
    n: int
    dados: list[PontoSerie]


class WorldBankEnvioOut(BaseModel):
    id: str
    n: int
    paises: list[str]
    indicadores: list[str]
    ano_inicio: int | None = None
    ano_fim: int | None = None


class WorldBankOut(BaseModel):
    id: str
    fonte: str
    data_extracao: str
    pais: str | None = None
    indicador: str | None = None
    inicio: int | None = None
    fim: int | None = None
    n: int
    dados: list[dict[str, Any]]


class MetaOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    meta: str | float | int | None = None
    onu: str | None = None
    brasil: str | None = None
    justificativa: str | None = None
    conceitos: str | None = None
    indicadores: str | None = None
    fonte: str | None = None
    data_extracao: str | None = None


class MetasOut(BaseModel):
    fonte: str
    n: int
    dados: list[MetaOut]


class MetaDetalheOut(BaseModel):
    fonte: str
    dados: MetaOut


class FatosOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    fonte_serie: str | None = None
    codigo_serie: str | None = None
    ano_quebra: int | None = None
    data_consulta: str | None = None
    unidade: str | None = None
    serie: dict[str, Any] | None = None
    ranking: dict[str, Any] | None = None
    fonte_ranking: str | None = None
    data_atualizacao_wb: str | None = None


# ---------------------------------------------------------------- análise de texto (TP4, Etapa 3)
MIN_CARACTERES_TEXTO = 50
MAX_CARACTERES_TEXTO = 2000
AVISO_RESUMO = (
    "Resumo gerado por modelo de linguagem; sujeito a revisão humana antes de ser usado como fato."
)


class PedidoTexto(BaseModel):
    """O que a API ACEITA em POST /processar_texto. Campo a mais é recusado (422)."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "texto": "A indústria de transformação perdeu participação no PIB brasileiro "
                             "nas últimas décadas, segundo a série do Ipeadata.",
                    "tipo_analise": "resumo",
                }
            ]
        },
    )

    texto: str = Field(
        min_length=MIN_CARACTERES_TEXTO,
        max_length=MAX_CARACTERES_TEXTO,
        description=f"O texto a resumir, de {MIN_CARACTERES_TEXTO} a {MAX_CARACTERES_TEXTO} caracteres.",
    )
    tipo_analise: Literal["resumo"] = Field(
        default="resumo", description="A análise pedida. Por enquanto, só o resumo."
    )

    @field_validator("texto")
    @classmethod
    def sem_espacos_nas_pontas(cls, valor: str) -> str:
        limpo = valor.strip()
        if len(limpo) < MIN_CARACTERES_TEXTO:
            raise ValueError(f"O texto precisa ter pelo menos {MIN_CARACTERES_TEXTO} caracteres, sem contar espaços nas pontas.")
        return limpo


class ResultadoResumo(BaseModel):
    """O que a API PROMETE devolver em POST /processar_texto (200)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tipo_analise": "resumo",
                    "texto": "A indústria de transformação perdeu participação no PIB brasileiro "
                             "nas últimas décadas, segundo a série do Ipeadata.",
                    "resumo": "A indústria de transformação perdeu participação no PIB brasileiro, segundo o Ipeadata.",
                    "motor": "Qwen/Qwen3-0.6B",
                    "aviso": AVISO_RESUMO,
                }
            ]
        }
    )

    tipo_analise: Literal["resumo"] = Field(description="A análise feita.")
    texto: str = Field(description="O texto processado, sem espaços nas pontas.")
    resumo: str = Field(min_length=1, description="O resumo gerado pelo modelo.")
    motor: str = Field(description="Qual modelo gerou o resumo (nome no Hugging Face).")
    aviso: str = Field(description="Ressalva sobre o resultado: foi gerado por modelo e precisa de revisão.")


# ---------------------------------------------------------------- chat com memória (TP5)
MAX_CARACTERES_PERGUNTA = 500
MAX_CARACTERES_MENSAGEM = 5000
MAX_MENSAGENS_HISTORICO = 40
MAX_CARACTERES_CONTEXTO = 150_000


class MensagemChat(BaseModel):
    """Uma fala da conversa: do usuário (`user`) ou do assistente (`assistant`)."""

    model_config = ConfigDict(extra="forbid")

    papel: Literal["user", "assistant"] = Field(description="Quem falou.")
    conteudo: str = Field(
        min_length=1,
        max_length=MAX_CARACTERES_MENSAGEM,
        description=f"O texto da fala, até {MAX_CARACTERES_MENSAGEM} caracteres.",
    )


class PedidoChat(BaseModel):
    """O que a API ACEITA em POST /chat. Campo a mais é recusado (422)."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "pergunta": "E em 2010?",
                    "historico": [
                        {"papel": "user", "conteudo": "A indústria perdeu participação desde 1995?"},
                        {"papel": "assistant", "conteudo": "Sim, de 16,81% em 1995 para 11,77% em 2025."},
                    ],
                    "contexto": "### Participação da indústria de transformação no PIB do Brasil\n"
                                "Fonte: Ipeadata\nano,% do PIB\n2025,11.77\n2010,14.97\n1995,16.81",
                }
            ]
        },
    )

    pergunta: str = Field(
        min_length=1,
        max_length=MAX_CARACTERES_PERGUNTA,
        description=f"A pergunta do usuário, até {MAX_CARACTERES_PERGUNTA} caracteres.",
    )
    historico: list[MensagemChat] = Field(
        default_factory=list,
        max_length=MAX_MENSAGENS_HISTORICO,
        description="As falas anteriores da conversa, da mais antiga à mais recente. "
        "Só as últimas 6 trocas seguem ao modelo.",
    )
    contexto: str = Field(
        min_length=1,
        max_length=MAX_CARACTERES_CONTEXTO,
        description="As tabelas que a página mostra, em texto, com fonte e nota. "
        "O assistente só responde com o que está aqui.",
    )

    @field_validator("pergunta")
    @classmethod
    def pergunta_sem_espacos_nas_pontas(cls, valor: str) -> str:
        limpo = valor.strip()
        if not limpo:
            raise ValueError("A pergunta não pode ficar em branco.")
        return limpo


class RespostaChat(BaseModel):
    """O que a API PROMETE devolver em POST /chat (200)."""

    resposta: str = Field(min_length=1, description="O texto do assistente.")
    motor: str = Field(description="Qual modelo da OpenAI gerou a resposta.")
    numeros_nao_verificados: list[str] = Field(
        description="Números da resposta que não estão nas tabelas, na pergunta, nem são o resultado de uma conta."
    )
    contas_conferidas: list[str] = Field(
        description='Contas que o código refez e confirmou, por exemplo "1,11 = 14,97 − 13,86".'
    )
    fontes: list[str] = Field(description="A fonte de cada tabela enviada, sem repetição.")
    aviso: str = Field(description="Ressalva: a resposta foi gerada por modelo e precisa de revisão humana.")
