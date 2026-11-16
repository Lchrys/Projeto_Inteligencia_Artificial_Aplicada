# Deployment (TDSP)

Este README foi redigido com apoio de IA (Claude Opus 5.5 e Claude Haiku 5.5) e revisado pelo autor.

A aplicação Streamlit está em Scripts/app.py, ponto de entrada do
Streamlit Community Cloud. A API FastAPI (Code/api/main.py) roda só em
ambiente local. No Cloud, Início, Série histórica, Comparação
internacional e Contexto ODS 9 leem as fontes direto (fallback em
Scripts/cliente_api.py).

## Ambiente

Python 3.13 no desenvolvimento local (`.venv`) e Python 3.12 no Streamlit
Community Cloud. Dependências em requirements.txt.

No Cloud, fastapi, uvicorn, torch, transformers e httpx são instalados, mas
não executados: a API só roda na máquina de quem a usa. O torch vem da versão só
de CPU do PyTorch (`--extra-index-url` no requirements.txt), para o build não
baixar CUDA. A versão fixada, 2.15.0, tem build de CPU para Python 3.12 e 3.13,
em Windows e Linux (verificado no índice do PyTorch).

## Execução local (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python Code/data_acquisition/scrape_ods9.py
uvicorn Code.api.main:app --reload
```

Em outro terminal:

```
streamlit run Scripts/app.py
```

A URL da API no painel é http://127.0.0.1:8000, substituível por API_URL em
`.streamlit/secrets.toml`. Sem a API no ar, as páginas mostram
"Origem: leitura direta" e a página Fontes e método avisa (isso não é
erro do painel publicado).

## Publicação

Branch main, arquivo principal Scripts/app.py, dependências em
requirements.txt. SIDRA e Ipeadata são APIs públicas; o World Bank entra
pelo upload do usuário (CSV de exemplo em Data/raw/). A FastAPI local não
sobe no Cloud.
`.streamlit/secrets.toml` e `.env` ficam de fora do Git. O modelo de linguagem
roda na máquina local e não usa chave de provedor.
