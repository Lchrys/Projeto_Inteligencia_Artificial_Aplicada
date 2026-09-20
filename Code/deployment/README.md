# Deployment (TDSP)

A aplicação está em Scripts/app.py (Streamlit), que é também o ponto de
entrada do deploy.

## Ambiente

Python 3.14 no desenvolvimento local e Python 3.12 no Streamlit Community
Cloud, onde a versão é escolhida nas configurações da aplicação. As
dependências são as mesmas nos dois ambientes, fixadas em requirements.txt
(streamlit, pandas, requests, ipeadatapy, beautifulsoup4, wordcloud e
matplotlib).

## Execução local (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python Code/data_acquisition/scrape_ods9.py
streamlit run Scripts/app.py
```

O scraping roda antes do primeiro start porque a página Contexto ODS 9 lê
Data/raw/ods9_metas.csv e Data/raw/ods9_corpus.txt. Os dois arquivos estão
versionados, então a etapa só é necessária para atualizar a extração.

## Publicação

A branch main do repositório é a origem do deploy no Streamlit Community
Cloud: arquivo principal Scripts/app.py e dependências em requirements.txt. Não há
variável de ambiente nem segredo a configurar: SIDRA e Ipeadata são APIs
públicas, e o World Bank entra por upload do usuário. O .gitignore reserva
.streamlit/secrets.toml caso isso mude.
