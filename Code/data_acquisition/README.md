# Data Acquisition (TDSP)

A aquisição de dados do projeto tem três formas. O Selenium não entra nesta
etapa; a decisão está em Docs/Data_Summary_Report.md.

Resumo. Fichas e ressalvas: Docs/Data_Summary_Report.md.

## 1. API consultada pelo dashboard

IBGE/SIDRA (tabela 1846, últimos quatro trimestres) e Ipeadata (SCN10_VAITY10)
são consultados ao vivo em Scripts/nucleo.py. O painel envolve essas funções
com cache de uma hora em Scripts/dados.py. A API FastAPI do projeto
(Code/api/main.py) usa o mesmo núcleo.

## 2. Scraping em script separado

O texto das metas do ODS 9 na página do Ipea é extraído com Beautiful Soup:

python Code/data_acquisition/scrape_ods9.py

Saídas: Data/raw/ods9_metas.csv e Data/raw/ods9_corpus.txt. Esses arquivos
alimentam GET /ods9/metas na API e a aba Corpus da página Contexto ODS 9.

## 3. Arquivo exportado do DataBank

O World Development Indicators é exportado manualmente do DataBank
(https://databank.worldbank.org/source/world-development-indicators) e salvo em
Data/raw/world_bank_setorial.csv. O dashboard não lê esse arquivo sozinho:
ele é o CSV de exemplo. Depois do upload na página Comparação internacional,
o painel converte o formato largo do DataBank em formato longo.

Para refazer o export, marque no DataBank: os países desejados na aba Country;
na aba Series os indicadores NV.AGR.TOTL.ZS, NV.IND.TOTL.ZS, NV.IND.MANF.ZS,
NV.SRV.TOTL.ZS, NV.IND.MANF.KD.ZG e TX.VAL.TECH.MF.ZS; e o período na aba Time.

O Banco Central (SGS) está mapeado no Data Summary Report, mas não entra na
extração desta etapa.
