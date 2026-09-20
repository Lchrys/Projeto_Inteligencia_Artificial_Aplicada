# Data / raw

Arquivos brutos, sem transformação. Toda extração externa é feita fora do
dashboard. O ODS 9 é lido pelo app a partir desta pasta; o World Bank só entra
depois do upload na página Comparação internacional, usando o CSV desta pasta como exemplo.

## ODS 9 (scraping com Beautiful Soup)

Gerados por `Code/data_acquisition/scrape_ods9.py`.

- `ods9_metas.csv`: as 8 metas do ODS 9 (9.1 a 9.c) extraídas da página do Ipea,
  com código, redação da ONU, redação brasileira, justificativa, conceitos,
  indicadores, fonte e data de extração.
- `ods9_corpus.txt`: texto concatenado das metas. A nuvem e a frequência usam
  por padrão a meta selecionada; o corpus completo permanece como opção.

## World Bank (export do DataBank)

Exportados manualmente do DataBank (World Development Indicators), em
https://databank.worldbank.org/source/world-development-indicators.

- `world_bank_setorial.csv`: exemplo para o serviço de upload da página
  Comparação internacional. 10 economias
  (Brasil, Estados Unidos, China, Rússia, Índia, Itália, França, Reino Unido,
  Alemanha e Japão) × 6 indicadores, de 1960 a 2025. Formato do DataBank:
  uma linha por país e série, uma coluna por ano (`1960 [YR1960]`), ausências
  como `..` e três linhas de rodapé no fim do arquivo.
- `world_bank_setorial_metadata.csv`: repete os dados e anexa, a partir da
  linha 67, a ficha técnica de cada série (definição longa, fonte, unidade,
  periodicidade, método de agregação, limitações e licença CC BY 4.0). Não é
  lido pelo app; serve de documentação para o Data Summary Report.

Indicadores incluídos: `NV.AGR.TOTL.ZS`, `NV.IND.TOTL.ZS`, `NV.IND.MANF.ZS`,
`NV.SRV.TOTL.ZS`, `NV.IND.MANF.KD.ZG` e `TX.VAL.TECH.MF.ZS`.

Este arquivo também é o exemplo oferecido para download na página Comparação
internacional do painel, para testar o serviço de upload com um CSV desta
mesma fonte.

Dois cuidados no uso, tratados no código:

- O DataBank grava `0` onde o dado não existe em algumas séries de participação
  (o Brasil aparece com 0% de 1960 até o fim dos anos 1970). O painel converte
  esses zeros em ausência nos indicadores `.ZS`.
- A transformação brasileira cai de 23,7% para 14,5% do PIB entre 1994 e 1995
  por mudança de referência das Contas Nacionais, não por desindustrialização.
  O painel avisa quando o período selecionado atravessa 1995.
