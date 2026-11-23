# Deployment (TDSP)

Este README foi redigido com apoio de IA (Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5) e revisado pelo autor.

O projeto roda na máquina de quem o usa: a API FastAPI (`Code/api/main.py`) e o painel Streamlit (`Scripts/app.py`).
O painel sobe a API sozinho ao abrir (`garantir_api`, em `Scripts/cliente_api.py`), e `python iniciar.py` prepara o
ambiente e sobe o painel de uma vez. O chat com IA e a aba Resumo exigem a API; as demais páginas leem os dados direto se
ela não estiver no ar (fallback em `Scripts/cliente_api.py`).

## Ambiente

Python 3.13 no desenvolvimento local (`.venv`); a seção 5 do README da raiz lista as versões aceitas. Dependências em `requirements.txt`.

O torch vem da versão só de CPU do PyTorch (`--extra-index-url` no `requirements.txt`), para a instalação não baixar
CUDA. A versão fixada, 2.15.0, tem build de CPU para Python 3.12 e 3.13, em Windows e Linux (verificado no índice do
PyTorch).

## Execução local (Windows)

Os passos de instalação, download do modelo e subida da API e do painel estão na seção 5 do README da raiz.

## Dados e segredos

SIDRA e Ipeadata são APIs públicas; o World Bank entra pelo upload do usuário (CSV de exemplo em `Data/raw/`).
`.streamlit/secrets.toml` e `.env` ficam de fora do Git. O modelo de linguagem local (Qwen, aba Resumo) roda na
máquina de quem usa e não usa chave.

## Chat com IA (TP5)

O chat no fim das páginas Panorama setorial, Série histórica e Comparação internacional usa a API da OpenAI pela
rota `POST /chat` da API FastAPI e precisa de `OPENAI_API_KEY` no `.env` (modelo em `.env.example`), que a API lê a
cada pedido. Se a API não subir sozinha, a página mostra o comando para subi-la à mão; sem a chave, a API responde 503 e o chat
mostra o aviso de chave não configurada. Nos dois casos o restante do painel segue normal. A chave nunca vai para o repositório.
