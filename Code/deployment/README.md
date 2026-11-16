# Deployment (TDSP)

Este README foi redigido com apoio de IA (Claude Opus 5.5 e Claude Haiku 5.5) e revisado pelo autor.

A aplicação Streamlit está em Scripts/app.py, ponto de entrada do
Streamlit Community Cloud. A API FastAPI (Code/api/main.py) roda só em
ambiente local. No Cloud, Início, Série histórica, Comparação
internacional e Corpus e resumos leem as fontes direto (fallback em
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

Os passos de instalação, download do modelo e subida da API e do painel estão na seção 5 do README da raiz.

## Publicação

Branch main, arquivo principal Scripts/app.py, dependências em
requirements.txt. SIDRA e Ipeadata são APIs públicas; o World Bank entra
pelo upload do usuário (CSV de exemplo em Data/raw/). A FastAPI local não
sobe no Cloud.
`.streamlit/secrets.toml` e `.env` ficam de fora do Git. O modelo de linguagem
roda na máquina local e não usa chave de provedor.
