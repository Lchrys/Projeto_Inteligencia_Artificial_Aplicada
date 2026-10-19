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
Indicators do World Bank. A comparação internacional é alimentada pelo CSV
que o usuário envia no painel, a partir do export do DataBank disponível em
`Data/raw/`. A API FastAPI local consulta essas fontes (GET) e recebe o
CSV do DataBank (POST /world-bank), gravado em `Data/processed/`
depois da validação. Início, Série histórica, Comparação internacional e
Contexto ODS 9 consomem a API quando ela está no ar e caem na leitura
direta quando não está.

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

O problema de negócio continua a evidência oficial dispersa. Nesta etapa
o painel também oferece acesso programático às séries e aos textos, pela
API FastAPI local (`Code/api/`, com modelos Pydantic e routers). Início,
Série histórica, Comparação internacional e Contexto ODS 9 consomem
essas rotas (`Scripts/cliente_api.py`). Se o serviço não responder (caso
do Streamlit Community Cloud), a mesma função cai na leitura direta em
`Scripts/nucleo.py`. Cada página indica a origem do dado.

O recorte continua o indicador 9.2.1 e as metas do ODS 9. O Panorama
usa o acumulado dos últimos quatro trimestres e trata a transformação
como subsetor ("dos quais"), não como quarto setor. A Comparação
internacional só mostra filtros e gráficos depois que o usuário envia o
CSV (o de exemplo em `Data/raw/` ou outro export do DataBank); com a API
no ar, o arquivo passa por POST /world-bank. A decisão de não usar
Selenium está no Data Summary Report.

## Entregas por etapa

Entregue no TP2: ambiente e estrutura TDSP; controle de versão em Git, com repositório no GitHub e `.gitignore` do ambiente virtual e dos segredos; painel publicado no Streamlit Community Cloud a partir da branch main (link no início do [README.MD](../README.MD)); extração via API de IBGE/SIDRA e Ipeadata; scraping da página ODS 9 do Ipea em script separado, com CSV e TXT em `Data/raw/`; World Development Indicators exportado do DataBank para `Data/raw/` como exemplo; interface Streamlit interativa com cache e estado de sessão; serviço de upload e download de CSV na página Comparação internacional, em que o arquivo enviado passa a alimentar os filtros e os gráficos da comparação internacional; download das tabelas oficiais, do recorte filtrado e do CSV de exemplo, com fonte, código da série e data de extração anexados; nuvem de palavras e frequência a partir do conteúdo extraído da web, com recorte na meta selecionada.

Entregue no TP3: API FastAPI local com modelos de resposta e routers; Início, Série histórica, Comparação internacional e Contexto ODS 9 consomem a API, com fallback para leitura direta; menu em seções; POST /world-bank recebe o CSV do DataBank e GET /world-bank/{id} o consulta; aba Corpus na Contexto ODS 9 (metas extraídas); Panorama em quatro trimestres, com a transformação isolada da indústria; Comparação internacional alimentada pelo CSV enviado pelo usuário; lógica compartilhada em `Scripts/nucleo.py`; envios do DataBank em `Data/processed/world_bank_envios/`; decisão documentada de não usar Selenium; preparação concreta para LLM; critérios de sucesso verificados na página Fontes e método.

Previsto para etapas posteriores: uso de LLM (Q&A, resumo das justificativas e relatório a partir de `/fatos/resumo`); indicador 9.2.2 (emprego na indústria sobre o emprego total, PNAD Contínua no SIDRA) para dar evidência ao pilar Social da meta 9.2; ampliação do corpus textual em `Data/raw/` (Carta de Conjuntura do Ipea, releases do PIB do IBGE e resumos das referências); participação em volume, além da participação a preços correntes; Banco Central/SGS como leitura de curto prazo; indicadores de complexidade (alta e média-alta intensidade tecnológica, 9.b.1).

Indicadores de sucesso: maior intervalo histórico possível nas APIs; comparação de agropecuária, indústria e serviços (e subsetores, quando possível); completude acima de 90% dos anos com valor na série do indicador 9.2.1 a partir de 1995, verificada na Série histórica (anos com valor sobre anos do intervalo); cada tabela baixada indica fonte, código da série e data de extração; soma setorial coerente com o valor adicionado a preços básicos, verificada no Panorama (agropecuária + indústria + serviços = VA; VA + impostos = PIB), sem exigir 100% do PIB a preços de mercado; consistência com a literatura econômica no tema, verificada no Data Summary Report; rotas da API descritas em `/docs` e em `Code/api/README.md`.

## Preparação para IA

Não há modelo de linguagem nesta etapa. Cada caso de uso da etapa
seguinte tem dado de entrada, rota, página de destino e critério de
avaliação:

| Caso | Dado de entrada | Rota | Página | Critério de avaliação |
|---|---|---|---|---|
| Q&A | Metas do ODS 9 (`ods9_metas.csv`) | GET /ods9/metas | Contexto ODS 9 (abas Meta e Corpus) | A resposta cita o código da meta usado |
| Resumo | Campo justificativa de cada meta | GET /ods9/metas/{codigo} | Contexto ODS 9 | O texto resumido cobre só a justificativa da meta pedida |
| Relatório | Último valor, variação desde 1995, máximo, ranking (entre as economias do CSV de exemplo, não mundial) | GET /fatos/resumo | Início | Nenhum número fora do JSON; o LLM só redige; o ranking usa `universo` e `nota` |

Classificação de sentimentos não entra no plano: as fontes desta etapa
são séries oficiais e textos institucionais (metas do ODS, justificativas
do Ipea), não opiniões de redes sociais ou noticiário. O ganho analítico
está em Q&A, resumo e relatório a partir de números já calculados.

O corpus atual (oito metas do ODS 9) é o mínimo para ensaiar Q&A. Na
etapa de LLM ele deve ser ampliado com notas de conjuntura, releases do
PIB e resumos da literatura, em arquivos em `Data/raw/`.

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
  A página Fontes e método avisa e o restante do painel segue lendo as
  fontes oficiais diretamente.
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
