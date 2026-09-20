# Project Charter: monitor-desindustrializacao

## Tese do projeto

O recorte, a definição de desindustrialização e a divergência entre as
redações da ONU e do Brasil para a meta 9.2 estão na seção 1 de
[README.MD](../README.MD). As referências estão em
[Referencias.md](Referencias.md).

O painel mede o componente "em proporção do PIB" do indicador 9.2.1 da
ONU. O componente per capita não entra nesta etapa.

## Escopo

O projeto, no conjunto, é um dashboard da participação da indústria no PIB brasileiro: agropecuária, indústria e serviços; subsetores industriais quando a fonte permitir; série oficial do IBGE/SIDRA e do Ipeadata; comparação internacional do
indicador de indústria de transformação no PIB a partir do World Development
Indicators do World Bank.

Não entra neste projeto (fora do escopo):

- Microdados de empresas.
- Recorte estadual ou municipal (o recorte é o Brasil).
- Emprego, salário, informalidade ou CAGED/RAIS: o painel não exibe
  essas séries nesta etapa (o emprego justifica o pilar Social, mas
  ainda não é indicador operacional). O indicador 9.2.2 da ONU
  (emprego na indústria sobre o emprego total) é o outro lado da meta
  9.2 e é o caminho previsto para dar evidência ao pilar Social em
  etapa posterior.
- O componente per capita do indicador 9.2.1.
- Avaliação causal de política industrial, crédito, câmbio ou tarifária.
- Inflação, juros, balança comercial ou mercado financeiro como tema
  central.
- Emissões, energia ou licenciamento ambiental da indústria.
- Previsão ou modelo preditivo da desindustrialização.

## Objetivos

- Tornar visível a trajetória da participação setorial no PIB
  brasileiro, com a indústria de transformação isolada do agregado
  industrial.
- Documentar fontes oficiais com hierarquia declarada no Data Summary Report:
  IBGE/SIDRA e Ipeadata por API, World Bank por arquivo exportado do DataBank
  e ODS 9 do Ipea por scraping.
- Extrair o texto das metas do ODS 9 na página do Ipea (Beautiful Soup) para contextualizar o indicador 9.2.1.
- Alinhar a solução ao ODS 9.2 e ao pilar Social do ESG.

## Entregas por etapa

Entregue nesta etapa: ambiente e estrutura TDSP; extração via API de IBGE/SIDRA e Ipeadata; scraping da página ODS 9 do Ipea em script separado, com CSV e TXT em `Data/raw/`; World Development Indicators exportado do DataBank para `Data/raw/` como exemplo; interface Streamlit interativa com cache e estado de sessão; serviço de upload e download de CSV na página Comparação internacional, em que o arquivo enviado passa a alimentar os filtros e os gráficos da comparação internacional; download das tabelas oficiais, do recorte filtrado e do CSV de exemplo, com fonte, código da série e data de extração anexados; nuvem de palavras e frequência a partir do conteúdo extraído da web, com recorte na meta selecionada.

Previsto para etapas posteriores: série histórica trimestral do SIDRA; participação em volume, além da participação a preços correntes; emprego industrial (indicador 9.2.2) para dar evidência ao pilar Social; Banco Central/SGS como leitura de curto prazo; indicadores de complexidade (alta e média-alta intensidade tecnológica, 9.b.1); controle de versão e deploy publicado.

Indicadores de sucesso: maior intervalo histórico possível nas APIs; comparação de agropecuária, indústria e serviços (e subsetores, quando possível); completude acima de 90% dos anos com valor na série do indicador 9.2.1 a partir de 1995 (exibida no painel); cada tabela baixada indica fonte, código da série e data de extração; soma setorial coerente com o valor adicionado a preços básicos, sem exigir 100% do PIB a preços de mercado; consistência com a literatura econômica no tema, verificada no Data Summary Report.

## Stakeholders

- Gestores de política industrial e de desenvolvimento econômico:
  acompanham a participação setorial no PIB.
- Federações e entidades da indústria: acompanham como a indústria
  evolui no PIB.
- Pesquisadores de economia industrial: usam a série histórica para
  análise comparada.
- Áreas de ESG e relações institucionais: situam o tema no ODS 9.2
  a partir da participação da indústria no PIB.
- Estudantes e demais interessados no tema.

## Riscos

- Indisponibilidade temporária das APIs (SIDRA, Ipeadata). A comparação
  internacional depende do arquivo enviado pelo usuário, e por isso não
  depende da disponibilidade dessas APIs: se SIDRA e Ipeadata caírem, o
  painel mantém a página Comparação internacional e a página Contexto ODS 9.
- Defasagem do arquivo do World Bank em relação à divulgação mais recente: o
  painel mostra a data de atualização registrada no próprio export.
- Revisão metodológica das Contas Nacionais (mudança de ano de referência).
- CSV enviado pelo usuário fora do formato esperado.
- Mudança no HTML da página do Ipea (o scraping deixa de achar as metas).
- Confundir o agregado "indústria" com a indústria de transformação, o que
  altera a conclusão sobre desindustrialização.
- Ler a participação a preços correntes como se fosse variação de volume,
  quando parte do movimento vem do preço relativo dos setores.
