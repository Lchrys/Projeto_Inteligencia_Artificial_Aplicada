# Project Charter: monitor-desindustrializacao

## Tese do projeto

O recorte, a definição de desindustrialização e a divergência entre as
redações da ONU e do Brasil para a meta 9.2 estão na seção 1 de
[README.MD](../README.MD). As referências estão em
[Referencias.md](Referencias.md).

O painel mede o componente "em proporção do PIB" do indicador 9.2.1 da
ONU. O componente per capita não entra nesta etapa.

O problema de negócio permanece a evidência oficial dispersa. Nesta etapa o
painel também oferece acesso programático às mesmas séries e textos, pela
API FastAPI local, e deixa o corpus e os indicadores calculados prontos para
consulta em linguagem natural na etapa de LLM.

## Escopo

O projeto, no conjunto, é um dashboard da participação da indústria no PIB brasileiro: agropecuária, indústria e serviços; subsetores industriais quando a fonte permitir; série oficial do IBGE/SIDRA e do Ipeadata; comparação internacional do
indicador de indústria de transformação no PIB a partir do World Development
Indicators do World Bank. A comparação internacional é alimentada pelo CSV que
o usuário envia no painel, a partir do export do DataBank disponível em
`Data/raw/`. A API FastAPI local consulta essas fontes (GET) e recebe
documentos textuais (POST /documentos), gravados em `Data/processed/`
depois da validação. Início, Série histórica e Contexto ODS 9 consomem
a API quando ela está no ar e caem na leitura direta quando não está.

Não entra neste projeto (fora do escopo):

- Microdados de empresas.
- Recorte estadual ou municipal (o recorte é o Brasil).
- Avaliação causal de política industrial, crédito, câmbio ou tarifária.
- Inflação, juros, balança comercial ou mercado financeiro como tema
  central.
- Emissões, energia ou licenciamento ambiental da indústria.
- Previsão ou modelo preditivo da desindustrialização.
- Coleta por Selenium: ver a decisão em
  [Data_Summary_Report.md](Data_Summary_Report.md).

Não entra nesta etapa (adiado, não descartado):

- Emprego, salário, informalidade ou CAGED/RAIS: o painel não exibe
  essas séries (o emprego justifica o pilar Social, mas ainda não é
  indicador operacional). O indicador 9.2.2 da ONU (emprego na
  indústria sobre o emprego total) é o outro lado da meta 9.2 e é o
  caminho previsto para dar evidência ao pilar Social.
- O componente per capita do indicador 9.2.1.
- Integração de LLM (resumo, Q&A e relatório narrativo). A preparação
  está na seção Preparação para IA; a implementação fica para a etapa
  seguinte.

## Objetivos

- Tornar visível a trajetória da participação setorial no PIB
  brasileiro, com a indústria de transformação isolada do agregado
  industrial.
- Documentar fontes oficiais com hierarquia declarada no Data Summary Report:
  IBGE/SIDRA e Ipeadata por API, World Bank por arquivo exportado do DataBank
  e ODS 9 do Ipea por scraping.
- Extrair o texto das metas do ODS 9 na página do Ipea (Beautiful Soup) para contextualizar o indicador 9.2.1.
- Expor as séries e os textos por uma API FastAPI local, com rotas GET e POST
  documentadas em `/docs`.
- Alinhar a solução ao ODS 9.2 e ao pilar Social do ESG.

## Revisão no TP3

O TP2 reuniu as séries oficiais num painel. O TP3 não acrescenta um
console ao lado disso: as páginas que já existiam passam a consumir a
API FastAPI (`Scripts/cliente_api.py`). Se o serviço não responder (caso
do Streamlit Community Cloud), a mesma função cai na leitura direta em
`Scripts/nucleo.py`. Cada página indica a origem do dado.

O problema de negócio ganha o acesso programático às séries e aos
textos. Não houve coleta nova: o recorte continua o indicador 9.2.1 e
as metas do ODS 9 já extraídas. A página Corpus textual foi absorvida
pela Contexto ODS 9. O POST da API ficou só em documentos textuais; o
upload de CSV do DataBank permanece na Comparação internacional.

## Entregas por etapa

Entregue no TP2: ambiente e estrutura TDSP; controle de versão em Git, com repositório no GitHub e `.gitignore` do ambiente virtual e dos segredos; painel publicado no Streamlit Community Cloud a partir da branch main (link no início do [README.MD](../README.MD)); extração via API de IBGE/SIDRA e Ipeadata; scraping da página ODS 9 do Ipea em script separado, com CSV e TXT em `Data/raw/`; World Development Indicators exportado do DataBank para `Data/raw/` como exemplo; interface Streamlit interativa com cache e estado de sessão; serviço de upload e download de CSV na página Comparação internacional, em que o arquivo enviado passa a alimentar os filtros e os gráficos da comparação internacional; download das tabelas oficiais, do recorte filtrado e do CSV de exemplo, com fonte, código da série e data de extração anexados; nuvem de palavras e frequência a partir do conteúdo extraído da web, com recorte na meta selecionada.

Entregue no TP3: as páginas Início, Série histórica e Contexto ODS 9 passam a consumir a API FastAPI local, com fallback para leitura direta; menu em seções; página API e dados para status e POST /documentos; aba Corpus na Contexto ODS 9; lógica compartilhada em `Scripts/nucleo.py`; documentos em `Data/processed/documentos.csv`; decisão documentada de não usar Selenium; preparação concreta para LLM.

Previsto para etapas posteriores: uso de LLM (Q&A, resumo das justificativas e relatório a partir de `/fatos/resumo`); série histórica trimestral do SIDRA; participação em volume, além da participação a preços correntes; emprego industrial (indicador 9.2.2) para dar evidência ao pilar Social; Banco Central/SGS como leitura de curto prazo; indicadores de complexidade (alta e média-alta intensidade tecnológica, 9.b.1).

Indicadores de sucesso: maior intervalo histórico possível nas APIs; comparação de agropecuária, indústria e serviços (e subsetores, quando possível); completude acima de 90% dos anos com valor na série do indicador 9.2.1 a partir de 1995, verificada na Série histórica (anos com valor sobre anos do intervalo); cada tabela baixada indica fonte, código da série e data de extração; soma setorial coerente com o valor adicionado a preços básicos, verificada no Panorama (agropecuária + indústria + serviços = VA; VA + impostos = PIB), sem exigir 100% do PIB a preços de mercado; consistência com a literatura econômica no tema, verificada no Data Summary Report; rotas da API descritas em `/docs` e em `Code/api/README.md`.

## Preparação para IA

Não há modelo de linguagem nesta etapa. Cada caso de uso da etapa
seguinte tem dado de entrada, rota, página de destino e critério de
avaliação:

| Caso | Dado de entrada | Rota | Página | Critério de avaliação |
|---|---|---|---|---|
| Q&A | Metas do ODS 9 (`ods9_metas.csv`) e `documentos.csv` | GET /ods9/metas, GET /documentos | Contexto ODS 9 (abas Meta e Corpus) | A resposta cita o código da meta (ou o id do documento) usado |
| Resumo | Campo justificativa de cada meta | GET /ods9/metas/{codigo} | Contexto ODS 9 | O texto resumido cobre só a justificativa da meta pedida |
| Relatório | Último valor, variação desde 1995, máximo, ranking (entre as economias do CSV de exemplo, não mundial) | GET /fatos/resumo | Início | Nenhum número fora do JSON; o LLM só redige; o ranking usa `universo` e `nota` |

A chave do provedor de LLM fica em `.streamlit/secrets.toml` ou `.env`,
ambos ignorados pelo Git. Não há chave neste repositório.

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
- API FastAPI local fora do ar: o Streamlit Community Cloud não a executa.
  A página API e dados avisa e o restante do painel segue lendo as fontes
  oficiais diretamente.
- Defasagem do arquivo do World Bank em relação à divulgação mais recente: o
  painel mostra a data de atualização registrada no próprio export.
- Revisão metodológica das Contas Nacionais (mudança de ano de referência).
- CSV enviado pelo usuário fora do formato esperado na página Comparação internacional.
- Mudança no HTML da página do Ipea (o scraping deixa de achar as metas).
- Confundir o agregado "indústria" com a indústria de transformação, o que
  altera a conclusão sobre desindustrialização.
- Ler a participação a preços correntes como se fosse variação de volume,
  quando parte do movimento vem do preço relativo dos setores.
- Na etapa de LLM: número inventado pelo modelo se o relatório não partir
  de `/fatos/resumo`; interpretar `posicao_brasil` como ranking mundial, quando
  o campo é a posição entre as economias do CSV de exemplo (ver `universo` e
  `nota` no JSON); custo e limite de uso da API do provedor.
