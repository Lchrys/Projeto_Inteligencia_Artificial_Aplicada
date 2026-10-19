"""Modelos Pydantic de entrada e saída da API."""

from typing import Any

from pydantic import BaseModel, ConfigDict


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
