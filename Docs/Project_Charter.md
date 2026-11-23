# Project Charter: monitor-desindustrializacao

## Tese do projeto

O recorte, a definição de desindustrialização e a divergência entre as
redações da ONU e do Brasil para a meta 9.2 estão na seção 1 de
[README.MD](../README.MD). As referências estão em
[Referencias.md](Referencias.md).

O painel mede o componente "em proporção do PIB" do indicador 9.2.1 da
ONU. O componente per capita não entra no TP3.

O problema de negócio permanece a evidência oficial dispersa. No TP3 o
painel também oferece acesso programático às mesmas séries e textos, pela
API FastAPI local, e deixa o corpus e os indicadores calculados prontos para
consulta em linguagem natural na etapa de LLM.

## Revisão no TP5

**Problema de negócio.** A evidência oficial sobre a desindustrialização está dispersa
(IBGE, Ipeadata, World Bank, Ipea) e exige conhecimento técnico para ser lida. No TP5 o
projeto fecha o ciclo: cada página de dados (Panorama setorial, Série histórica e Comparação
internacional) ganha um chat com memória que responde, em linguagem natural, a perguntas sobre
o que a própria página mostra, com os filtros aplicados.

**Por que dados, IA e engenharia de prompts se encaixam no problema.**

- *Dados:* as séries oficiais coletadas e processadas pelo painel são a única fonte de verdade.
  O assistente recebe as tabelas da página, em texto, com fonte e notas de método.
- *IA:* o LLM traduz essas tabelas em explicação para quem não é técnico (gestores, entidades
  de classe, áreas de ESG, estudantes), reduzindo o custo de chegar à evidência. A memória
  conversacional permite aprofundar ("e em 2024?") sem repetir o contexto.
- *Engenharia de prompts:* um prompt de sistema genérico define o papel do assistente e impõe
  regras: responder só com as tabelas fornecidas, dizer o que falta quando o dado não existe,
  citar a fonte, respeitar as notas (preços correntes, quebra de 1995) e não prever nem
  recomendar política. O código ajuda o modelo: ordena as séries do ano mais recente ao mais
  antigo e calcula primeiro, último, mínimo e máximo de cada coluna.

**Alinhamento a ESG e ODS.** ODS 9, meta 9.2 (aumentar a participação da indústria no emprego e
no PIB até 2030), indicador 9.2.1: o painel mostra a parte do PIB, que caiu de 16,81% em 1995 para
11,77% em 2025 na transformação (Ipeadata), contra a direção da meta.
- *Ambiental:* não é medido (emissões e eficiência de recursos, meta 9.4, estão fora do painel).
- *Social:* a meta liga a indústria a emprego e produtividade, mas o painel não tem série de emprego
  (indicador 9.2.2 fora do escopo); ele mostra só a perda de peso no PIB, como contexto, e não afirma
  perda de empregos.
- *Governança:* dados públicos rastreáveis, fonte das tabelas exibida pelo código sob toda resposta,
  números conferidos por código e texto enviado ao modelo à vista (revisão humana).
**Simplicidade de uso:** filtros, gráfico e chat na mesma página, sem escolher modelo nem colar dados.

**Escolha do modelo.** A API da OpenAI é o motor, pela qualidade de conversa em português. O Qwen3-0.6B
do TP4 permanece na aba Resumo (resumo de textos, sem custo e sem internet); ele não sustenta uma
conversa com tabelas. O chat passa pela rota `POST /chat` da API FastAPI. Os dados enviados são públicos; a
chave fica fora do repositório.

**Critérios de sucesso do TP5.**

- Todo número da resposta existe nas tabelas da página ou na pergunta, ou é o resultado exato de uma conta
  (diferença, soma, variação percentual) entre valores que a resposta mostra (checagem por código, com teste
  automático); o que não for assim aparece como aviso.
- O assistente só vê o que a página mostra, com os filtros aplicados; sem o CSV do DataBank
  enviado, a Comparação internacional não tem dados nem chat.
- O assistente mantém o contexto entre perguntas e diz quando o dado não está na página.
- Toda resposta mostra a fonte: o código exibe, sob a resposta, a fonte das tabelas enviadas ao modelo, sem
  depender de o modelo citá-la (com teste automático). O prompt também pede a citação no texto, que
  aparece em 17 das 24 respostas dos casos reais (`Data/modeled/chat_openai_casos.csv`; detalhes em `Docs/Teste_do_chat.md`).
- Falha da API de IA (chave, limite, tempo) vira uma mensagem clara no chat, sem derrubar o
  painel; o painel sobe a API do projeto sozinho, e, se ela não subir, o chat mostra o comando para subi-la à mão.

**Fora do escopo no TP5:** previsão da desindustrialização, recomendações de política,
perguntas que cruzem fontes de páginas diferentes, indicador 9.2.2 e Banco Central/SGS.

## Escopo

O projeto, no conjunto, é um dashboard da participação da indústria no PIB brasileiro: agropecuária, indústria e serviços; subsetores industriais quando a fonte permitir; série oficial do IBGE/SIDRA e do Ipeadata; comparação internacional do
indicador de indústria de transformação no PIB a partir do World Development
Indicators do World Bank. A comparação internacional é alimentada pelo CSV
que o usuário envia no painel, a partir do export do DataBank disponível em
`Data/raw/`. A API FastAPI local consulta essas fontes (GET) e recebe o
CSV do DataBank (POST /world-bank), gravado em `Data/processed/`
depois da validação. Início, Série histórica, Comparação internacional e
Corpus e resumos consomem a API quando ela está no ar e caem na leitura
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

Fora do escopo do projeto:

- Emprego, salário, informalidade ou CAGED/RAIS: o painel não exibe
  essas séries (o emprego justifica o pilar Social, mas não é
  indicador do painel). O indicador 9.2.2 da ONU (emprego na
  indústria sobre o emprego total) é o outro lado da meta 9.2 e é o
  que daria evidência ao pilar Social; o projeto o documenta como limite.
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

O problema de negócio continua a evidência oficial dispersa. No TP3
o painel também oferece acesso programático às séries e aos textos, pela
API FastAPI local (`Code/api/`, com modelos Pydantic e routers). Início,
Série histórica, Comparação internacional e Corpus e resumos consomem
essas rotas (`Scripts/cliente_api.py`). Se o serviço não responder, a mesma função cai na leitura direta em
`Scripts/nucleo.py`. Cada página indica a origem do dado.

O recorte continua o indicador 9.2.1 e as metas do ODS 9. O Panorama
usa o acumulado dos últimos quatro trimestres e trata a transformação
como subsetor ("dos quais"), não como quarto setor. A Comparação
internacional só mostra filtros e gráficos depois que o usuário envia o
CSV (o de exemplo em `Data/raw/` ou outro export do DataBank); com a API
no ar, o arquivo passa por POST /world-bank. A decisão de não usar
Selenium está no Data Summary Report.

## Entregas por etapa

Entregue no TP2: ambiente e estrutura TDSP; controle de versão em Git, com repositório no GitHub e `.gitignore` do ambiente virtual e dos segredos; extração via API de IBGE/SIDRA e Ipeadata; scraping da página ODS 9 do Ipea em script separado, com CSV e TXT em `Data/raw/`; World Development Indicators exportado do DataBank para `Data/raw/` como exemplo; interface Streamlit interativa com cache e estado de sessão; serviço de upload e download de CSV na página Comparação internacional, em que o arquivo enviado passa a alimentar os filtros e os gráficos da comparação internacional; download das tabelas oficiais, do recorte filtrado e do CSV de exemplo, com fonte, código da série e data de extração anexados; nuvem de palavras e frequência a partir do conteúdo extraído da web, com recorte na meta selecionada.

Entregue no TP3: API FastAPI local com modelos de resposta e routers; Início, Série histórica, Comparação internacional e Corpus e resumos consomem a API, com fallback para leitura direta; menu em seções; POST /world-bank recebe o CSV do DataBank e GET /world-bank/{id} o consulta; aba Corpus na página Corpus e resumos (metas extraídas); Panorama em quatro trimestres, com a transformação isolada da indústria; Comparação internacional alimentada pelo CSV enviado pelo usuário; lógica compartilhada em `Scripts/nucleo.py`; envios do DataBank em `Data/processed/world_bank_envios/`; decisão documentada de não usar Selenium; preparação concreta para LLM; critérios de sucesso verificados na página Fontes e método.

Entregue no TP4: `POST /processar_texto` na API FastAPI local, com um modelo de linguagem local (`Qwen/Qwen3-0.6B`, na CPU) que gera resumos em português; modelos de entrada e saída em `Code/api/models.py`; códigos 422, 502, 503, 504 e 500 documentados e testados; corpus textual ampliado com os resumos das referências (`Code/data_acquisition/scrape_referencias.py`, em `Data/raw/referencias_resumos.csv`). A escolha do modelo está em `Docs/Escolha_do_modelo.md`.

Entregue no TP5: chat com memória no fim das páginas Panorama setorial, Série histórica e Comparação internacional, com a OpenAI como motor (o Qwen3-0.6B segue na aba Resumo); contexto de cada chat montado com as tabelas da própria página (`Scripts/contextos.py`); assistente genérico em `Code/modeling/assistente.py`; testes automáticos e 24 casos reais; artefatos do TDSP atualizados (ver "Revisão no TP5" acima e no Data Summary Report).

Fora do escopo do projeto: indicador 9.2.2 (emprego na indústria sobre o emprego total, PNAD Contínua no SIDRA) para dar evidência ao pilar Social da meta 9.2; ampliação do corpus textual em `Data/raw/`: resumos das referências já coletados por `Code/data_acquisition/scrape_referencias.py` (SciELO, Springer e FGV; Tregenna e Palma bloqueados, Rowthorn excluído por decisão); Carta de Conjuntura do Ipea e releases do PIB do IBGE não coletados (releases bloqueadas para coleta automatizada); participação em volume, além da participação a preços correntes; Banco Central/SGS como leitura de curto prazo; indicadores de complexidade (alta e média-alta intensidade tecnológica, 9.b.1).

Indicadores de sucesso: maior intervalo histórico possível nas APIs; comparação de agropecuária, indústria e serviços (e subsetores, quando possível); completude acima de 90% dos anos com valor na série do indicador 9.2.1 a partir de 1995, verificada na Série histórica (anos com valor sobre anos do intervalo); cada tabela baixada indica fonte, código da série e data de extração; soma setorial coerente com o valor adicionado a preços básicos, verificada no Panorama (agropecuária + indústria + serviços = VA; VA + impostos = PIB), sem exigir 100% do PIB a preços de mercado; consistência com a literatura econômica no tema, verificada no Data Summary Report; rotas da API descritas em `/docs` e em `Code/api/README.md`.

## Preparação para IA

Não há modelo de linguagem no TP3. Cada caso de uso da etapa
seguinte tem dado de entrada, rota, página de destino e critério de
avaliação:

| Caso | Dado de entrada | Rota | Página | Critério de avaliação |
|---|---|---|---|---|
| Q&A | Metas do ODS 9 (`ods9_metas.csv`) | GET /ods9/metas | Corpus e resumos (abas Meta e Corpus) | A resposta cita o código da meta usado |
| Resumo | Campo justificativa de cada meta | GET /ods9/metas/{codigo} | Corpus e resumos | O texto resumido cobre só a justificativa da meta pedida |
| Relatório | Último valor, variação desde 1995, máximo, ranking (entre as economias do CSV de exemplo, não mundial) | GET /fatos/resumo | Início | O Início mostra o último valor, a variação desde 1995 e o máximo do JSON; o ranking fica na rota, com `universo` e `nota`, e não aparece no painel. No TP5, a redação por LLM foi substituída pelo chat com memória de cada página |

Classificação de sentimentos não entra no plano: as fontes desta etapa
são séries oficiais e textos institucionais (metas do ODS, justificativas
do Ipea), não opiniões de redes sociais ou noticiário. O ganho analítico
está em Q&A, resumo e relatório a partir de números já calculados.

O corpus atual (oito metas do ODS 9) é o mínimo para ensaiar Q&A. Na
etapa de LLM ele deve ser ampliado com notas de conjuntura, releases do
PIB e resumos da literatura, em arquivos em `Data/raw/`.

No TP3/TP4, o modelo de linguagem roda na máquina local e não usa chave de provedor. No TP5, o assistente usa a API da OpenAI, com a chave fora do repositório (ver "Revisão no TP5").
Não há chave neste repositório.

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
  painel mantém a página Comparação internacional e a página Corpus e resumos.
- API FastAPI local fora do ar: a página Fontes e método avisa, as páginas de dados seguem lendo as
  fontes oficiais diretamente e o chat avisa que precisa da API.
- Defasagem do arquivo do World Bank em relação à divulgação mais recente: o
  painel mostra a data de atualização registrada no próprio export.
- Revisão metodológica das Contas Nacionais (mudança de ano de referência).
- CSV enviado pelo usuário fora do formato esperado na página Comparação internacional.
- Mudança no HTML da página do Ipea (o scraping deixa de achar as metas).
- TP5: o assistente inventar números ou errar a leitura de uma tabela longa (mitigação: checagem de números por código,
  contexto restrito ao que a página mostra, resumo calculado pelo código e revisão humana); falha, limite ou custo da API da
  OpenAI (mitigação: histórico curto, resposta limitada e erros tratados com mensagem clara); vazamento da chave
  (mitigação: `.env`, nada no Git).
- Confundir o agregado "indústria" com a indústria de transformação, o que
  altera a conclusão sobre desindustrialização.
- Ler a participação a preços correntes como se fosse variação de volume,
  quando parte do movimento vem do preço relativo dos setores.
- Na etapa de LLM: número inventado pelo modelo (no TP5, tratado pela conferência de números por código e
  pelo contexto restrito às tabelas da página); interpretar `posicao_brasil` de `/fatos/resumo` como ranking
  mundial, quando o campo é a posição entre as economias do CSV de exemplo (ver `universo` e `nota` no JSON,
  e o painel não exibe o ranking); custo e limite de uso da API do provedor.
