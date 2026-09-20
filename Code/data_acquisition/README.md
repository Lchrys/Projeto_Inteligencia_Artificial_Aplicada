# Data Acquisition (TDSP)

A aquisição de dados do projeto tem três formas.

## 1. API consultada pelo dashboard

IBGE/SIDRA (tabela 1846) e Ipeadata (SCN10_VAITY10) são consultados ao vivo em
Scripts/dados.py, com cache de uma hora.

## 2. Scraping em script separado

O texto das metas do ODS 9 na página do Ipea é extraído com Beautiful Soup:

python Code/data_acquisition/scrape_ods9.py

Saídas: Data/raw/ods9_metas.csv e Data/raw/ods9_corpus.txt.

## 3. Arquivo exportado do DataBank

O World Development Indicators é exportado manualmente do DataBank
(https://databank.worldbank.org/source/world-development-indicators) e salvo em
Data/raw/world_bank_setorial.csv. O dashboard não lê esse arquivo sozinho:
ele é o CSV de exemplo. Depois do upload na página Comparação internacional, o painel
converte o formato largo do DataBank em formato longo.

Para refazer o export, marque no DataBank: os países desejados na aba Country;
na aba Series os indicadores NV.AGR.TOTL.ZS, NV.IND.TOTL.ZS, NV.IND.MANF.ZS,
NV.SRV.TOTL.ZS, NV.IND.MANF.KD.ZG e TX.VAL.TECH.MF.ZS; e o período na aba Time.
O painel aceita qualquer recorte de país, indicador e período desta fonte,
porque os filtros são derivados do próprio arquivo. O gráfico de composição
setorial empilha os indicadores escolhidos pelo usuário.

O Banco Central (SGS) está mapeado no Data Summary Report, mas não entra na
extração desta etapa.
