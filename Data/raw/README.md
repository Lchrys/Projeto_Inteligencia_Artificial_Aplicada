# Data / raw

Este README foi redigido com apoio de IA (Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5) e revisado pelo autor.

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

## Referências sobre desindustrialização (TP4)

Gerados por `Code/data_acquisition/scrape_referencias.py`, a partir das URLs de
`referencias_urls.txt` (uma por linha, curadas à mão).

- `referencias_urls.txt`: as páginas dos três periódicos usados (SciELO, Springer e FGV).
- `referencias_resumos.csv`: título, autores, ano, periódico, DOI, resumo, idioma do resumo, licença e data de coleta de cada referência.
- `oreiro_feijo_2010_introducao.txt`: a seção INTRODUÇÃO do artigo de Oreiro e Feijó (2010), em português, com citação e licença (CC BY-NC 4.0) no cabeçalho. Usada na medição de modelos e na aba Resumo.

A licença de cada linha depende do periódico. Ver "Estudos publicados" em `Docs/Data_Summary_Report.md`.

