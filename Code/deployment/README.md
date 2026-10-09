# Deployment (TDSP)

A aplicação Streamlit está em Scripts/app.py, que é o ponto de entrada do
deploy no Streamlit Community Cloud. A API FastAPI está em Code/api/main.py e
roda só em ambiente local. No Cloud, Início, Série histórica e Contexto ODS 9
leem as fontes direto (fallback em Scripts/cliente_api.py).

## Ambiente

Python 3.14 no desenvolvimento local e Python 3.12 no Streamlit Community
Cloud, onde a versão é escolhida nas configurações da aplicação. As
dependências são as mesmas nos dois ambientes, fixadas em requirements.txt
(streamlit, pandas, requests, ipeadatapy, beautifulsoup4, wordcloud,
matplotlib, fastapi e uvicorn). No Cloud, fastapi e uvicorn são instalados,
mas não executados: o serviço publicado é só o Streamlit.

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

O scraping roda antes do primeiro start porque a página Contexto ODS 9 lê
Data/raw/ods9_metas.csv e Data/raw/ods9_corpus.txt. Os dois arquivos estão
versionados, então a etapa só é necessária para atualizar a extração.

A URL da API no painel é http://127.0.0.1:8000, substituível por API_URL em
`.streamlit/secrets.toml`. Sem a API no ar, as páginas mostram
"Origem: leitura direta" e a página API e dados avisa.

## Publicação

A branch main do repositório é a origem do deploy no Streamlit Community
Cloud: arquivo principal Scripts/app.py e dependências em requirements.txt.
Não há variável de ambiente nem segredo obrigatório: SIDRA e Ipeadata são APIs
públicas, o World Bank entra por upload do usuário, e a FastAPI local não
sobe no Cloud. O .gitignore reserva `.streamlit/secrets.toml` e `.env` para a
chave do LLM na etapa seguinte.
