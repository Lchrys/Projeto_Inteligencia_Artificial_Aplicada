# API do monitor (FastAPI)

API local para consultar as séries oficiais e os textos do ODS 9, e para
receber o CSV do DataBank. O painel consome estas rotas em Início, Série
histórica, Comparação internacional e Contexto ODS 9
(`Scripts/cliente_api.py`). Se o serviço não responder, as páginas leem
direto de `Scripts/nucleo.py`. O Streamlit Community Cloud não sobe esta API.

Organização (padrão da disciplina): `main.py` cria a aplicação;
`models.py` declara os modelos Pydantic de entrada e saída
(`response_model` em todas as rotas); `routers/` separa séries e ODS 9.
A série do Ipeadata fica em cache de uma hora.

Documentação interativa gerada pelo FastAPI: http://127.0.0.1:8000/docs

## Como subir (Windows, na raiz do repositório)

```
.venv\Scripts\activate
uvicorn Code.api.main:app --reload
```

O serviço fica em http://127.0.0.1:8000. Em outro terminal, `streamlit run Scripts/app.py`.

A URL pode ser alterada no painel por `API_URL` em `.streamlit/secrets.toml`.
O padrão é `http://127.0.0.1:8000`.

## Rotas

### GET /saude

Confirma que a API está no ar. O painel consulta esta rota a cada 30 segundos
(cache). Resposta: `SaudeOut`.

```
curl http://127.0.0.1:8000/saude
```

### GET /serie/transformacao

Série SCN10_VAITY10 (Ipeadata), indicador 9.2.1. Recorte opcional por ano.
Consumida pela Série histórica e pelo gráfico da Início. Resposta: `SerieOut`.

```
curl "http://127.0.0.1:8000/serie/transformacao?inicio=1995&fim=2025"
```

### POST /world-bank

Recebe o CSV exportado do DataBank, valida o formato, converte para formato
longo e grava em `Data/processed/world_bank_envios/{id}.csv`. Sucesso
devolve 201 (`WorldBankEnvioOut`) com o identificador. Arquivo fora do
formato devolve 400. A Comparação internacional consome esta rota no upload.

```
curl -X POST http://127.0.0.1:8000/world-bank ^
  -F "arquivo=@Data/raw/world_bank_setorial.csv"
```

### GET /world-bank/{id}

Consulta um envio gravado pelo POST. Filtros opcionais por país (código
ISO3), indicador, início e fim. NV.IND.MANF.ZS é o indicador 9.2.1. Envio
inexistente devolve 404. Resposta: `WorldBankOut`.

```
curl "http://127.0.0.1:8000/world-bank/{id}?pais=BRA&indicador=NV.IND.MANF.ZS&inicio=1995"
```

### GET /ods9/metas e GET /ods9/metas/{codigo}

Metas extraídas da página ODS 9 do Ipea. Consumidas pela página Contexto ODS 9.
Respostas: `MetasOut` e `MetaDetalheOut`.

```
curl http://127.0.0.1:8000/ods9/metas
curl http://127.0.0.1:8000/ods9/metas/9.2
```

### GET /fatos/resumo

Indicadores já calculados (último valor, variação desde 1995, máximo e ranking).
O ranking é a posição do Brasil entre as economias do CSV de exemplo do
DataBank (`Data/raw/world_bank_setorial.csv`) no último ano com valor do
Brasil — não um ranking mundial. O JSON traz `universo`,
`paises_no_arquivo`, `paises_com_valor_no_ano`, `paises_sem_valor_no_ano` e
`nota`. A página Início consome esta rota. Na etapa de LLM, este JSON é a
entrada do relatório: o modelo só redige. Resposta: `FatosOut`.

```
curl http://127.0.0.1:8000/fatos/resumo
```
