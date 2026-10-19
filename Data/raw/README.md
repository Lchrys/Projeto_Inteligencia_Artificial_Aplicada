# Data / raw

Arquivos brutos, sem transformação. Toda extração externa é feita fora do
dashboard. Fichas e ressalvas: Docs/Data_Summary_Report.md.

## ODS 9 (scraping com Beautiful Soup)

Gerados por `Code/data_acquisition/scrape_ods9.py`.

- `ods9_metas.csv`: as 8 metas do ODS 9 (9.1 a 9.c) extraídas da página do Ipea.
- `ods9_corpus.txt`: texto concatenado das metas.

## World Bank (export do DataBank)

- `world_bank_setorial.csv`: 10 economias × 6 indicadores, 1960–2025.
  Exemplo para download; filtros e gráficos só aparecem depois do upload
  na Comparação internacional.
- `world_bank_setorial_metadata.csv`: ficha técnica das séries. Não é lido
  pelo app.
