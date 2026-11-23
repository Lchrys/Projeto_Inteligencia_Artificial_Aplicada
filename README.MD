# Monitor Brasileiro de Desindustrialização

Painel para acompanhar a participação da indústria no PIB brasileiro, alinhado ao
ODS 9.2 e ao pilar Social do ESG. Roda na máquina de quem o usa, com a API FastAPI e o painel Streamlit (seção 5).

Este README foi redigido com apoio de IA (Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5) e revisado pelo autor.

**Etapas:** TP2 (painel Streamlit) → TP3 (API FastAPI, scraping, upload) → TP4 (API integrada a um LLM local) → **TP5 (chat com memória em cada página, OpenAI)**.

## Sumário

1. [Problema de negócio](#1-problema-de-negócio)
2. [Organização (CRISP-DM e TDSP)](#2-organização-crisp-dm-e-tdsp)
3. [Entregas do TP2, TP3 e TP4](#3-entregas-do-tp2-tp3-e-tp4)
4. [TP5: chat com IA em cada página](#4-tp5-chat-com-ia-em-cada-página)
5. [Como rodar (Windows)](#5-como-rodar-windows)
6. [Estrutura de diretórios](#6-estrutura-de-diretórios)

---

## 1. Problema de negócio

O Brasil perde participação da indústria de transformação no PIB há décadas
(desindustrialização; Tregenna, 2009; Oreiro e Feijó, 2010; Morceiro, 2021 — ver
`Docs/Referencias.md`). Isso desloca ocupações para serviços de baixa produtividade e
reduz a capacidade de inovar e exportar. A evidência oficial existe, mas está dispersa. O
projeto entrega um painel acessível, e uma API, que reúnem essa trajetória a partir de
fontes oficiais (IBGE/SIDRA, Ipeadata, World Bank, Ipea).

**Metas de sucesso:** série do indicador 9.2.1 com valor em mais de 90% dos anos desde 1995;
cada tabela com fonte, código da série e data de extração; soma setorial coerente com o valor
adicionado a preços básicos; dados do IBGE compatíveis com Ipeadata e literatura; quebras
metodológicas sinalizadas; séries da API sempre com a divulgação oficial mais recente; rotas
descritas em `/docs`.

**ESG e ODS:** pilar Social (menos empregos formais e de maior produtividade), com
diálogo com o Ambiental (industrialização sustentável) e a Governança (dados públicos). Atende
ao **ODS 9, meta 9.2** (indicador 9.2.1, em proporção do PIB); o ODS 8 entra só como contexto.

**Recorte:** indicador = indústria de transformação (SIDRA 90693), não a indústria total
(90691). Séries a preços correntes. A ONU pede aumentar a participação da indústria; o Ipea
desloca o foco para produtividade e complexidade — o painel mede o indicador da ONU e exibe o
texto do Ipea como ressalva. Detalhes em `Docs/Data_Summary_Report.md`.

**Público:** formuladores de política industrial, federações e entidades de classe,
pesquisadores, estudantes de economia, áreas de ESG e demais interessados.

## 2. Organização (CRISP-DM e TDSP)

CRISP-DM e TDSP são usados em conjunto; a estrutura de pastas segue o TDSP.

| Fase (CRISP-DM / TDSP) | Artefato |
|---|---|
| Entendimento do negócio / Business Understanding | Seção 1 e `Docs/Project_Charter.md` (escopo, critérios, interessados) |
| Entendimento dos dados / Data Acquisition | `Docs/Data_Summary_Report.md`, `Code/data_exploration/`; aquisição por API (`Scripts/nucleo.py`), scraping (`Code/data_acquisition/`) e upload do DataBank |
| Preparação dos dados | `Scripts/nucleo.py` (cacheado em `Scripts/dados.py`); brutos em `Data/raw/`, recebidos por POST em `Data/processed/` |
| Modelagem / Modeling | Sem modelo preditivo (o charter exclui previsão). Cálculo das participações e comparações; no TP4, o LLM local de resumo (`Code/modeling/resumidor.py`); no TP5, o assistente com a OpenAI (`Code/modeling/assistente.py`) |
| Avaliação / Customer Acceptance | Página *Fontes e método* confere os critérios de sucesso; o avaliador acadêmico exerce o papel do cliente |
| Implantação / Deployment | Painel (`Scripts/app.py`), API (`Code/api/main.py`), notas em `Code/deployment/` |

Papéis: líder (escopo, charter); Data Scientist/Engineer (fontes, indicadores); Solution
Architect (estrutura TDSP, ambiente, arquitetura).

## 3. Entregas do TP2, TP3 e TP4

Painel Streamlit multipágina (`Scripts/app.py` e `Scripts/pages/`; ver `Scripts/README.md` e `Scripts/pages/README.md`)
e API FastAPI (`Code/api/`). Com a API no ar, o Início, a Série histórica, a Comparação internacional e o Corpus e resumos
a consomem e indicam a origem do dado ("API FastAPI" ou "leitura direta"); sem ela, leem as fontes diretamente. O Panorama
setorial lê a SIDRA direto, sem a API.

### 3.1 Painel e API (TP2 e TP3)

| Item | Onde / como |
|---|---|
| Ambiente e deploy | `requirements.txt` com versões fixas; `.gitignore` (`.venv/`, `.env`, segredos); Git; execução local do painel e da API, com `iniciar.py` (ver `Code/deployment/README.md`) |
| Interface | 6 páginas em 3 seções do menu. **Painel:** Início, *SIDRA (Panorama Setorial)*, *IPEA (Série Histórica)* (seletor de anos) e *Comparação Internacional* (upload CSV). **Contexto:** Corpus e resumos (meta, nuvem de palavras, aba Corpus e aba Resumo com o modelo local). **Método:** Fontes e método. Nos textos, as três páginas de dados aparecem pelo nome curto (Panorama setorial, Série histórica, Comparação internacional) |
| API FastAPI | `Code/api/main.py`, routers (ver `Code/api/routers/README.md`) e modelos Pydantic; GET de saúde, série, World Bank, metas ODS 9 e fatos/resumo; `POST /world-bank` (201). Cliente em `Scripts/cliente_api.py` |
| Web scraping | `Code/data_acquisition/scrape_ods9.py` (Beautiful Soup, sem Selenium: nenhuma fonte é dinâmica) grava `Data/raw/ods9_metas.csv` e `ods9_corpus.txt`; no TP4, `scrape_referencias.py` grava os resumos das referências (ver `Code/data_acquisition/README.md`) |
| Cache e sessão | `st.cache_data` (1 h nas consultas SIDRA/Ipeadata e nas respostas da API); CSV enviado em `st.session_state` |
| Upload e download | `st.file_uploader` (CSV do DataBank → `POST /world-bank`); downloads de exemplo, recorte filtrado, tabelas SIDRA/Ipeadata (com fonte, código e data), TXT do Ipea e corpus |
| Documentação | `Docs/Project_Charter.md`, `Docs/Data_Summary_Report.md`, READMEs por pasta |

### 3.2 LLM local (TP4)

A rota **`POST /processar_texto`** resume um texto (50 a 2.000 caracteres) com o
**[`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B)** (Apache 2.0, sem conta), executado na máquina do usuário,
em float32 na CPU, sem internet após o download. Na página *Corpus e resumos*, a aba **Resumo** usa essa rota para
resumir uma meta do ODS 9, um resumo de referência ou a introdução de Oreiro e Feijó (2010), em português.

- **Integração.** `Code/modeling/resumidor.py` carrega o modelo uma vez, na subida da API; `Code/api/routers/texto.py`
  expõe a rota; o painel a consome por `Scripts/cliente_api.py`. Medição (`Code/modeling/medir_modelo.py`, ver
  `Code/modeling/README.md`), no banco de 10 textos: 12–38 s por resumo (mediana 26 s), ~2,4 GB de RAM.
- **Ambiente e hardware** (passos na seção 5, passos 2, 7 e 5: instalar, baixar o modelo e subir o painel, que sobe a API; detalhes em `Code/api/README.md` e
  `Docs/Escolha_do_modelo.md`, seção 4). Bibliotecas: `transformers`, `torch` (só CPU, via `--extra-index-url` no
  `requirements.txt`), `huggingface_hub`, `fastapi` e `uvicorn`; `psutil` e `httpx` só em medição e testes. No Intel
  Core i5-1035G1, com 8 GB de RAM e sem GPU: float32 na CPU (~2,4 GB), modo de raciocínio do Qwen3 desligado
  (`enable_thinking=False`, pois o resumo só precisa da resposta) e, com o modelo em disco, funcionamento offline
  (`HF_HUB_OFFLINE=1`). O aviso de links simbólicos do cache Hugging Face no Windows é inofensivo.
- **Response Models.** Todas as rotas declaram `response_model` com modelos Pydantic em `Code/api/models.py`; os pedidos
  rejeitam campos extras. A rota de texto devolve o resumo em formato estruturado e documentado em `/docs`.
- **Tratamento de erros** (`Code/api/erros.py`, `Code/api/routers/texto.py`; declarados no `/docs` e cobertos por testes
  com modelo falso em `Code/api/tests/`):

  | Código | Cenário |
  |---|---|
  | 422 | texto com menos de 50 ou mais de 2.000 caracteres, campo extra ou tipo de análise inválido |
  | 502 | o modelo devolveu resumo vazio |
  | 503 | o modelo não carregou na subida (as demais rotas seguem no ar) |
  | 504 | geração acima de 120 s |
  | 500 | erro inesperado: mensagem com código de rastreio; o traceback fica só no log |

- **Escolha do modelo.** Critérios: desempenho (qualidade do resumo em português), custo computacional (cabe em 8 GB de
  RAM sem GPU) e acessibilidade (licença aberta, sem conta, ~1,5 GB). O Qwen2.5-1.5B-Instruct (~6,2 GB só de pesos) foi
  descartado antes da medição (travou a máquina). O Qwen2.5-0.5B-Instruct e o Qwen3-0.6B foram medidos num banco de 10
  textos (7 justificativas do ODS 9 e 3 resumos de referência; saídas em `Data/modeled/`): o Qwen3-0.6B foi escolhido
  porque errou menos nos textos do tema, e não por ser o mais rápido ou o mais leve. Justificativa, medições e erros: `Docs/Escolha_do_modelo.md`, que
  também registra o uso de IA.
- **Limites.** O resumo é gerado por modelo e exige revisão humana antes de ser usado como fato; textos em inglês podem
  gerar resumos que repetem o título. A rota de texto só existe com a API no ar; sem ela, a aba Resumo mostra
  "indisponível".
- **Observações do TP3 tratadas no TP4.** `cliente_api.py` com fallback e indicação da origem: feito, com uma diferença
  (a função nova `analisar_texto` não tem fallback: sem a API, a aba Resumo mostra "indisponível" e não indica a origem).
  Scraping do ODS 9 igual ao do TP2: tratado, e o projeto ganhou uma fonte e um script novos, o scraping das referências
  sobre desindustrialização (`Code/data_acquisition/scrape_referencias.py`).

### 3.3 Onde verificar cada critério do TP4

| Critério | Onde está | Como verificar |
|---|---|---|
| Integração funcional com o LLM | `Code/modeling/resumidor.py`, `Code/api/routers/texto.py` | Subir o painel (seção 5, passos 2, 5 e 7; ele sobe a API junto) e abrir http://127.0.0.1:8000/docs: testar `POST /processar_texto`. Ou, no painel (http://localhost:8501), aba **Resumo** em *Corpus e resumos* |
| Descrição detalhada da integração (ambiente, bibliotecas, hardware) | Seção 3.2, `Code/api/README.md`, `Docs/Escolha_do_modelo.md` (seção 4) | Ler as três; as bibliotecas estão em `requirements.txt` |
| Response Models | `Code/api/models.py` (`PedidoTexto`, `ResultadoResumo`) | Em /docs, ver os esquemas; enviar um texto com campo extra e conferir o 422 |
| Tratamento de erros | `Code/api/erros.py`, `Code/api/routers/texto.py`, `Code/api/tests/` | `.venv\Scripts\python.exe -m unittest discover -s Code\api\tests -t .` (cobre 422, 502, 503, 504 e 500) |
| Justificativa da escolha do modelo | `Docs/Escolha_do_modelo.md` (seções 2 e 3) | Ler a tabela de candidatos e a seção de justificativas; as medições estão em `Data/modeled/` |

## 4. TP5: chat com IA em cada página

O TP5 fecha o ciclo com a **memória conversacional** (opção 1 do enunciado). No fim das páginas *Panorama setorial*,
*Série histórica* e *Comparação internacional* há o chat **"Pergunte aos dados desta página"**: um assistente que lembra
a conversa e responde só com o que aquela página mostra, **com os filtros aplicados**. O motor é a **API da OpenAI**
(`gpt-4.1-mini`, trocável por `OPENAI_MODEL`).

### 4.1 Arquivos e fluxo

| O quê | Onde |
|---|---|
| Assistente genérico: prompt, memória, chamada à OpenAI, checagem de números | `Code/modeling/assistente.py` |
| Contexto de cada página (as tabelas que ela mostra, em texto) | `Scripts/contextos.py` (`contexto_serie`, `contexto_panorama`, `contexto_comparacao`) |
| Componente de chat reutilizável | `Scripts/chat_pagina.py` (`chat_da_pagina`); páginas com chat: `Scripts/pages/1_Panorama_setorial.py`, `2_Serie_historica.py` e `3_Comparacao_internacional.py` |
| Rota `POST /chat` da API e seus modelos | `Code/api/routers/chat.py`; `PedidoChat`, `MensagemChat` e `RespostaChat` em `Code/api/models.py`; cliente `conversar` em `Scripts/cliente_api.py` |
| Faixa do ciclo de dados | `Scripts/interface.py` (`faixa_ciclo`), usada no Início (`Scripts/app.py`) |
| Testes com OpenAI simulada | `Code/api/tests/test_assistente.py` e `test_chat.py` (ver `Code/api/tests/README.md`) |
| Teste com a OpenAI real: 24 casos | `Code/modeling/testar_assistente.py` → `Data/modeled/chat_openai_casos.csv`; relato em `Docs/Teste_do_chat.md` |
| Chave da OpenAI | `.env` na raiz (fora do Git; modelo em `.env.example`), lido pela API |
| Artefatos do TDSP | `Docs/Project_Charter.md` e `Docs/Data_Summary_Report.md` (seções "Revisão no TP5") |

**Por onde o chat chama a OpenAI.** O painel envia a pergunta, o histórico (até 40 falas) e o contexto da página para `POST /chat`
da API FastAPI, que chama o assistente e devolve `resposta`, `motor`, `numeros_nao_verificados`, `contas_conferidas`, `fontes` e `aviso`
(entrada fora do contrato responde 422; limites e exemplo em `Code/api/README.md`). O chat só funciona com a API FastAPI no ar:
o painel sobe a API sozinho ao abrir, e, se ela não subir, a página mostra o aviso e o comando para subi-la à mão. A API
não guarda conversa: o
histórico fica no painel (`st.session_state`) e vai a cada pedido.

**Fluxo completo, do dado ao insight** (ao lado de cada etapa, o arquivo onde ela acontece):

```
1. COLETA             Ipeadata (API) · IBGE SIDRA (API) · World Bank (CSV enviado) · Ipea ODS 9 e referências (scraping)
                                                  │
2. PROCESSAMENTO      Scripts/nucleo.py: limpeza, formato longo, zeros do DataBank como ausência,
   E ANÁLISE          participações setoriais e comparações, aviso da quebra de 1995
                                                  │
3. ACESSO             API FastAPI (Code/api) ──► Scripts/cliente_api.py
                      (sem a API: as páginas leem direto de nucleo.py; o chat e o resumo exigem a API)
                                                  │
4. APRESENTAÇÃO       Scripts/app.py e Scripts/pages/ (6 páginas): gráficos, tabelas e filtros
                                                  │
5. IA (CHAT)          Scripts/contextos.py: as tabelas da página, com os filtros, viram o contexto
                      Scripts/chat_pagina.py ──► POST /chat (Code/api/routers/chat.py)
                      Code/modeling/assistente.py: prompt, memória de 6 trocas, OpenAI (gpt-4.1-mini),
                      conferência dos números por código
                                                  │
                                                  ▼
                      Resposta na página: "Conta conferida", "Fonte das tabelas" e os dados enviados à vista

RESUMO LOCAL (TP4)    aba Resumo ──► POST /processar_texto ──► Qwen3-0.6B (carregado na subida da API)
```

### 4.2 Como a solução resolve o problema de negócio (ESG e ODS)

A evidência oficial sobre a desindustrialização está dispersa e pede conhecimento técnico para ser lida. Um gestor de
política industrial, uma federação ou uma área de ESG quer a resposta a perguntas como "a indústria perdeu participação
desde 1995?" ou "como o Brasil se compara à Alemanha em 2024?", com a fonte à vista. O chat entrega isso em linguagem
natural, ao lado do gráfico, e o usuário aprofunda sem repetir o contexto ("e em 2024?"). O impacto é reduzir o custo de
chegar à evidência oficial, não substituir a análise nem recomendar política.

**Insights a partir dos dados reais.** Os valores que o chat devolveu estão em `Data/modeled/chat_openai_casos.csv`
(rodada de 22/11/2026; casos numerados de 1 a 24, na ordem do arquivo; lista dos casos em `Docs/Teste_do_chat.md`):

- *Série histórica (Ipeadata):* a perda de participação desde 1995, o maior e o menor valor da série (casos 1 e 2).
- *Panorama setorial (SIDRA, acumulado de 3º trimestre de 2025 a 2º trimestre de 2026):* o peso de serviços, indústria,
  agropecuária e transformação (casos 10 a 12). Os valores mudam a cada divulgação trimestral do IBGE.
- *Comparação internacional (World Bank, CSV enviado):* Brasil, China e Alemanha em 2024 e o ano de 1990, em que só o
  Brasil tem dado (casos 17 e 19).

**ODS 9.** A meta 9.2 (texto em `Data/raw/ods9_metas.csv`, aba Meta da página Corpus e resumos) pede aumentar, até 2030, a
participação da indústria no emprego e no PIB. O painel mede a parte do PIB (indicador 9.2.1), e a Série histórica mostra
a transformação em queda desde 1995, na direção contrária à da meta (valores no CSV acima e em `Docs/Project_Charter.md`,
"Revisão no TP5"): o chat deixa o gestor ver isso, com a fonte, sem planilha.

**ESG.**
- *Ambiental (E):* não é medido (emissões e eficiência de recursos são o foco da meta 9.4).
- *Social (S):* a meta 9.2 liga a indústria a emprego, produtividade e condições de trabalho. O painel **não tem série de
  emprego** (o indicador 9.2.2 está fora do escopo), então não afirma quantos empregos se perderam: mostra a perda de peso
  no PIB, como sinal de contexto, e o usuário deve buscar o emprego em outra fonte.
- *Governança (G):* dados públicos rastreáveis, fonte das tabelas exibida pelo código sob toda resposta, números
  conferidos por código, aviso quando algo não bate e texto enviado ao modelo à vista na página.

**Simplicidade de uso.** Cada página tem os filtros, o gráfico e o chat juntos: o usuário pergunta sobre o que está
vendo, sem escolher modelo, colar dados ou sair da tela. As sugestões de pergunta e o botão "Nova conversa" bastam para
começar.

### 4.3 Engenharia de prompts, chave e custo

- **O assistente é genérico e não conhece nenhuma fonte.** Cada página entrega o CONTEXTO (`Scripts/contextos.py`, montado
  com as mesmas funções da página): as tabelas que ela mostra, com fonte e nota (unidade, preços correntes, mudança de
  referência de 1995). Uma pergunta nova (outro ano, país ou indicador) não exige código novo: basta o dado estar na tela.

  | Página | Contexto |
  |---|---|
  | Série histórica | A série do Ipeadata no intervalo do seletor de anos |
  | Panorama setorial | Composição do PIB por setor e subsetores da indústria (acumulado de quatro trimestres) e os valores trimestrais da SIDRA |
  | Comparação internacional | O CSV do DataBank que o usuário enviou, com os filtros aplicados: uma tabela por indicador, um país por coluna |

- **Tabelas fáceis de ler.** A célula sem valor é escrita "sem dado", em vez de vazia, para o modelo não contar vírgulas em
  tabelas largas. As séries temporais vão do ano mais recente ao mais antigo e trazem um "Resumo calculado" (primeiro,
  último, mínimo e máximo de cada coluna, com o ano), feito pelo código, para o modelo não varrer dezenas de linhas atrás
  de um extremo; o resumo é dado separadamente antes e depois de 1995.
- **Prompt** (`PROMPT_SISTEMA` em `Code/modeling/assistente.py`): responder só com as tabelas, com todo número escrito
  nelas; dizer o que falta quando o dado não está; citar a fonte; comparar citando os dois valores e calcular só diferença,
  soma ou variação percentual mostrando os valores usados e o resultado; usar a seleção na tela, o resumo calculado e o
  ano mais recente quando a pergunta não disser o ano; falar no passado; não recomendar política nem prever; recusar em
  uma frase o pedido de ignorar as regras, dizendo o que as tabelas mostram.
- **Verificação dos números.** Depois da resposta, o código confere cada número contra as tabelas e as falas do usuário (o
  que o próprio assistente disse antes não conta). Um número que não está nas tabelas só é aceito se for o resultado exato
  de uma **conta** (diferença, soma, variação percentual ou razão) entre dois valores que a própria resposta mostra e que
  estão nas tabelas: o código refaz a conta, e a página exibe "Conta conferida pelo código: 1,11 = 14,97 − 13,86". Sem os
  dois valores na resposta, ou com a conta errada, o número aparece como aviso. A checagem entende "11,77", "11.77",
  "3.277.790" e "712.716,0".
- **Memória e auditoria.** O histórico fica na sessão do usuário, separado por página; só as últimas 6 trocas seguem ao
  modelo, o que limita custo e contexto, e a resposta é limitada a 450 tokens. Cada chat tem o expander "Dados que o
  assistente recebe", com o texto exato enviado ao modelo. Só dados públicos (as tabelas da página) e a pergunta saem da
  máquina.
- **Por que a OpenAI e não o modelo local.** O Qwen3-0.6B (TP4) resume bem textos curtos, mas não sustenta uma conversa com
  memória e tabelas. A OpenAI dá qualidade de conversa em português e resposta em 1 a 3 s (0,9 a 2,6 s nos 24 casos reais,
  contra 12 a 38 s no modelo local). O chat **não usa o modelo local** nem o download do Qwen, que segue na aba Resumo.
- **Chave.** Crie o arquivo `.env` na raiz (modelo em `.env.example`; o Git o ignora) com `OPENAI_API_KEY=sua_chave_aqui`.
  A API lê a chave desse arquivo a cada pedido. Nunca a escreva em arquivo versionado. Sem chave, a API responde 503, o
  chat mostra a mensagem de chave não configurada e o resto do painel segue normal.
- **Integração e custo.** `requests` chama direto a API de *chat completions* da OpenAI (sem o SDK); `pandas` monta as
  tabelas do contexto; `streamlit` desenha o chat; nenhuma dependência nova no `requirements.txt`. Parâmetros
  (`Code/modeling/assistente.py`): `gpt-4.1-mini`, temperatura 0,2, no máximo 450 tokens na resposta, 6 trocas de
  memória, 60 s de tempo limite. Tamanho do contexto enviado a cada pergunta, medido com os dados do repositório: 0,8 mil
  caracteres na Série histórica (de 1995 em diante), 3,5 mil no Panorama setorial e 2,8 mil na Comparação internacional
  com os filtros padrão (Brasil, Alemanha, China e EUA, um indicador); com os 10 países e os 6 indicadores do CSV de
  exemplo, 37 mil. O custo cresce com o filtro, por isso o chat só envia o que a tela mostra.

### 4.4 Erros e testes

As falhas viram uma mensagem no chat, sem derrubar a página. O assistente (`ErroAssistente`) as classifica com um código
de status; a API os devolve como status HTTP de `POST /chat`, e o painel mostra a frase do `detail`:

| Código | Cenário |
|---|---|
| 503 | chave da OpenAI não configurada |
| 429 | limite de uso ou crédito da OpenAI esgotado |
| 502 | a OpenAI recusou a chave, falhou, ficou sem internet ou devolveu resposta vazia |
| 504 | a OpenAI não respondeu em 60 s |

A pergunta tem no máximo 500 caracteres. Se a API FastAPI estiver fora do ar, o chat não aparece: a página mostra o aviso e o
comando para subi-la à mão (se ela cair no meio da conversa, a mensagem do chat diz o mesmo).

**Testes automáticos** (`Code/api/tests/test_assistente.py` e `test_chat.py`, com a OpenAI simulada: sem rede nem chave)
cobrem o contexto, a memória, a checagem de números e de contas, os erros e a rota `POST /chat`.

**Teste com exemplos reais.** `Code/modeling/testar_assistente.py` roda **24 casos** contra a OpenAI, com os dados reais
e os filtros padrão de cada página (três conversas com memória: Série histórica 9 casos, Panorama setorial 6 e Comparação
internacional 9), e grava `Data/modeled/chat_openai_casos.csv` (pergunta, o que se esperava, resposta, tempo, números
fora das tabelas, contas conferidas e fonte exibida). Os casos cobrem valor de um ano, memória ("e em 2011?"), conta
("qual a diferença?"), ano ou dado fora da tela, previsão, pergunta fora do tema, premissa falsa e tentativa de forçar uma
resposta. A lista completa, as correções e o alcance do teste estão em `Docs/Teste_do_chat.md`.

**Resultado da última rodada** (`gpt-4.1-mini`): 24 respostas sem erro, de 0,9 a 2,6 s cada. Todas foram conferidas
contra o "esperado" do teste e todas o cumpriram. Nenhum número ficou fora das tabelas sem explicação. Em 3 respostas o modelo fez
contas (por exemplo, "qual a diferença?" entre 14,97% e 13,86%: 1,11 p.p.), 5 contas ao todo, e o código conferiu todas.
A fonte das tabelas aparece sob as 24 respostas (coluna `fontes_exibidas` do CSV); em 17 delas o modelo também a cita no
texto.

**O que o teste achou e foi corrigido.** Sete achados, todos corrigidos: resumos pré-calculados que falhavam em "e em
2024?"; três defeitos na checagem de números (vírgula do CSV, formato brasileiro e `$...$` lido como fórmula); busca
errada na série inteira; a regra que proibia contas; "E em 1990?" na Comparação (tabela larga e esparsa: a célula sem
valor virou "sem dado" e o modelo padrão passou para o `gpt-4.1-mini`, 5 de 5 repetições certas, contra 3 de 5 do
`gpt-4o-mini`); a fonte que dependia de o modelo citá-la (hoje o código a exibe sob toda resposta); e duas respostas
vazias de conteúdo (regras 2 e 11 do prompt). A redação do modelo varia a cada chamada; em toda chamada o código assegura
a conferência dos números e a exibição da fonte. Detalhe e alcance do teste: `Docs/Teste_do_chat.md`.

### 4.5 Limites

A resposta é gerada por modelo e exige revisão humana. O chat só vê o que a página mostra: para perguntar sobre outro ano,
país ou indicador, é preciso mudar o filtro; e a comparação internacional só existe depois do envio do CSV do DataBank.
Cada chat responde sobre a sua página, não sobre as outras. O assistente descreve o que os dados mostram, sem prever nem
recomendar política, e precisa de internet e de crédito na conta da OpenAI.

### 4.6 Onde verificar cada rubrica do TP5

| Rubrica | Onde está | Como verificar |
|---|---|---|
| Funcionalidade integrada ao dashboard | `Scripts/chat_pagina.py` e o fim das páginas 1, 2 e 3 | Abrir *IPEA (Série Histórica)*, descer até o chat e fazer duas perguntas seguidas (a segunda depende da primeira). Com a API no ar (seção 5, passo 4), `POST /chat` aparece no `/docs` e responde às perguntas do chat; sem a API, a página mostra o comando para subi-la |
| Dados coletados geram insights em ESG e ODS | `Scripts/contextos.py`, `Data/modeled/chat_openai_casos.csv` | Perguntar sobre a perda desde 1995 e abrir *Dados que o assistente recebe*; os números da resposta estão nesse texto |
| Ciclo completo de ciência de dados | Seção 4.1 (fluxo), faixa do ciclo no Início, `Docs/Data_Summary_Report.md` | Ler o fluxo e conferir cada arquivo |
| Justificativa de negócio, ESG e ODS | Seção 4.2 e `Docs/Project_Charter.md` ("Revisão no TP5") | Ler as duas |
| LLM de forma eficiente e alinhada ao objetivo | `Code/modeling/assistente.py`, seção 4.3 | Ver o prompt, a checagem de números e o limite de trocas; rodar `test_assistente.py` e `test_chat.py` |
| Dashboard claro e organizado | Gráficos e tabelas de cada página, com o chat logo abaixo | Abrir as páginas |
| Artefatos do TDSP atualizados | `Docs/Project_Charter.md`, `Docs/Data_Summary_Report.md` | Ler as seções "Revisão no TP5" |
| Simplicidade e fluidez | Perguntas sugeridas, botão *Nova conversa*, filtros da própria página, mensagens de erro claras, aviso de revisão | Usar uma página sem ler nada antes |

## 5. Como rodar (Windows)

Passo a passo, do zero até o assistente funcionando. Os comandos chamam o Python do `.venv` direto, então não é preciso
ativar o ambiente. Rode-os na pasta do projeto, no PowerShell ou no Prompt de Comando. **Caminho mínimo para ver o TP5:**
passos 1 a 6; o modelo local (passo 7) é **opcional**, pois só a aba Resumo o usa.

**Antes de começar:** Windows, com **Python 3.12, 3.13 ou 3.14** (testado com 3.13; o 3.15 não serve, porque o pandas
3.0.5 não tem pacote pronto para ele) e **Git**; **internet** na primeira execução (baixa as dependências) e sempre que o
painel consulta SIDRA e Ipeadata; e uma **chave da OpenAI com crédito** para o assistente (seção 4.3), a centavos por
conversa.

### 5.1 Passo a passo

1. **Obter o código:**
   ```
   git clone https://github.com/Lchrys/Projeto_Inteligencia_Artificial_Aplicada.git
   cd Projeto_Inteligencia_Artificial_Aplicada
   ```
2. **Ambiente e dependências** (uma vez; demora alguns minutos, porque inclui o PyTorch só de CPU):
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. **Chave da OpenAI.** Copie o modelo do arquivo e preencha a chave, sem aspas e sem espaços (`OPENAI_API_KEY=sua_chave_aqui`).
   O `.env` fica fora do Git, e a chave é lida a cada pedido, então não é preciso reiniciar nada depois de criá-lo:
   ```
   copy .env.example .env
   notepad .env
   ```
4. **API (sobe sozinha com o painel, passo 5).** O chat só funciona com ela no ar; Início, Série histórica, Comparação
   internacional e Corpus e resumos também a usam e, se ela cair, leem direto. O painel a sobe ao abrir (a primeira
   abertura leva uns 20 s a mais, porque a API carrega o modelo local do TP4; sem o modelo baixado, passo 7, ela sobe
   mesmo assim e só o resumo fica indisponível) e a encerra quando o painel termina. Documentação em
   http://127.0.0.1:8000/docs. Só rode o comando abaixo se quiser a API à parte (por exemplo com `--reload`, que recarrega
   a cada arquivo salvo) ou se ela não subir sozinha, caso em que a causa fica em `%TEMP%\monitor_api.log`:
   ```
   .venv\Scripts\python.exe -m uvicorn Code.api.main:app --reload
   ```
5. **Subir o painel** (e, com ele, a API). Ele abre em http://localhost:8501 (deixe o terminal aberto):
   ```
   .venv\Scripts\python.exe -m streamlit run Scripts/app.py
   ```
6. **Usar o chat.** No painel, abra **SIDRA (Panorama Setorial)**, **IPEA (Série Histórica)** ou **Comparação Internacional** (menu
   Painel) e desça até "Pergunte aos dados desta página".
   - Na primeira abertura, as páginas levam de 10 a 20 s (Ipeadata e SIDRA; depois, cache de 1 h). Clique numa pergunta
     sugerida ou escreva a sua (até 500 caracteres); a resposta leva de 1 a 3 s.
   - Faça uma **segunda pergunta de continuação** (por exemplo, "e em 2010?") para ver a memória funcionando.
   - O chat vê o que a página mostra, **com os filtros aplicados**: mude o intervalo (Série histórica) ou os países,
     indicadores e anos (Comparação internacional) para perguntar sobre outro recorte. A **Comparação internacional** só
     mostra dados e chat depois que você envia um CSV do DataBank (o de exemplo está em `Data/raw/world_bank_setorial.csv`
     e pode ser baixado na própria página).
   - **Dados que o assistente recebe** mostra o texto exato enviado ao modelo; **Nova conversa** apaga o histórico da página.
7. **(Opcional) Modelo local do TP4.** Só a aba **Resumo** da página *Corpus e resumos* e a rota `POST /processar_texto`
   usam o Qwen3-0.6B, e ela exige a API (passo 4). Baixe o modelo uma vez, com internet (~1,5 GB); sem ele, essa rota
   responde 503, e o assistente do TP5 não é afetado:
   ```
   .venv\Scripts\python.exe Code\modeling\baixar_modelo.py
   ```
8. **Conferir** (da raiz do projeto):
   ```
   .venv\Scripts\python.exe -m unittest discover -s Code\api\tests -t .
   ```
   Os testes do assistente e da rota `POST /chat` usam uma OpenAI simulada: não gastam crédito nem precisam de chave. Os de
   `test_texto.py` exigem que o `transformers` carregue (ver 5.3).

**Forma rápida (opcional).** `python iniciar.py` cria o ambiente e instala as dependências se ainda não existirem, confere
(e baixa, na primeira vez) o modelo local de ~1,5 GB e sobe o painel, que sobe a API junto, em
http://localhost:8501. Para parar, feche a janela. Ele **não cria o `.env`**: faça o passo 3 antes.

### 5.2 Testes com modelos reais e regeneração de dados (opcionais)

```
.venv\Scripts\python.exe Code\modeling\testar_assistente.py
```
Teste do assistente com a OpenAI real, 24 casos (precisa de chave e internet e gasta uma pequena quantia de crédito;
grava `Data/modeled/chat_openai_casos.csv`).

```
set RODAR_MODELO_REAL=1
.venv\Scripts\python.exe -m unittest Code.api.tests.test_modelo_real -v
```
Teste do modelo local real (demora cerca de 1 minuto; exige o passo 7).

```
.venv\Scripts\python.exe Code\data_acquisition\scrape_ods9.py
.venv\Scripts\python.exe Code\data_acquisition\scrape_referencias.py
```
Regerar os dados extraídos (já estão em `Data/raw/`, ver `Data/raw/README.md`).

### 5.3 Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| "Chave da OpenAI não configurada" | O `.env` não existe, está fora da raiz ou a linha está sem a chave. Refaça o passo 3 (a API lê o arquivo a cada pedido). |
| "A OpenAI recusou a chave" | Chave errada, com espaço ou aspas, ou revogada. |
| "Limite de uso ou crédito da OpenAI esgotado" | Falta crédito na conta da OpenAI. |
| O chat mostra "a API não está no ar" | O painel tenta subir a API sozinho e ela não respondeu (por exemplo, a porta 8000 está ocupada por outro programa). Veja `%TEMP%\monitor_api.log` ou suba-a à mão (passo 4) e recarregue a página (o painel confere a API a cada 30 s). |
| Aba Resumo indisponível | A API não está no ar (passo 4) ou o modelo não foi baixado (passo 7). |
| Página lenta na primeira abertura | Consulta ao Ipeadata e ao SIDRA. Aguarde; depois fica em cache por 1 h. |
| "Controle de Aplicativo bloqueou este arquivo" ao importar `regex`, `transformers` ou subir a API | Uma política de segurança do Windows bloqueou o pacote `regex`. As páginas funcionam sem a API (exceto o chat e a aba Resumo); para usar a API (e com ela o chat) ou a aba Resumo, libere o arquivo na política ou reinstale o pacote. |
| Porta 8501 ou 8000 em uso | Há outra instância aberta. Feche-a ou use outra porta (`--server.port` no Streamlit, `--port` no uvicorn). |

Sem a API, as páginas que a consomem mostram "Origem: leitura direta" e seguem funcionando; o chat e a aba Resumo exigem
a API.
Exemplos de chamadas e testes: `Code/api/README.md`.

## 6. Estrutura de diretórios

Cada pasta de código e de dados tem um README próprio.

```
Docs/                 # Project_Charter, Data_Summary_Report, Referencias, Escolha_do_modelo, Teste_do_chat (TP5 no Charter e no Data Summary Report)
Data/
    raw/              # dados brutos (inclui referências para o teste do modelo)
    processed/        # envios do POST /world-bank
    modeled/          # resumos das medições do modelo local e casos de teste do chat com IA
Code/
    api/              # FastAPI: main, models, erros, routers/ (series, ods9, texto, chat), tests/
    data_acquisition/ # scraping (ODS 9 e referências)
    data_exploration/ # entendimento e EDA (reservada)
    modeling/         # resumidor, baixar_modelo, medir_modelo; TP5: assistente, testar_assistente
    deployment/       # notas de implantação
Scripts/              # app.py, nucleo.py, dados.py, cliente_api.py, interface.py, contextos.py, chat_pagina.py, pages/ (6 páginas), assets/
iniciar.py            # sobe o ambiente, a API e o painel de uma vez (seção 5)
.env.example          # modelo do .env com a chave da OpenAI (o .env fica fora do Git)
requirements.txt
.gitignore
README.MD
```
