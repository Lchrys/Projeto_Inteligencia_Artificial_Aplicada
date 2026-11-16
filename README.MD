# Monitor Brasileiro de Desindustrialização

Painel para acompanhar a participação da indústria no PIB brasileiro, alinhado ao
ODS 9.2 e ao pilar Social do ESG. Aplicação publicada:
[Streamlit](https://projetointeligenciaartificialaplicada-bahhxlugo9rejaxkrd3njj.streamlit.app/)

Este README foi redigido com apoio de IA (Claude Opus 5.5 e Claude Haiku 5.5) e revisado pelo autor.

**Etapas:** TP2 (painel Streamlit) → TP3 (API FastAPI, scraping, upload) → **TP4 (API integrada a um LLM local)**.

## Sumário

1. [Problema de negócio](#1-problema-de-negócio)
2. [Organização (CRISP-DM e TDSP)](#2-organização-crisp-dm-e-tdsp)
3. [Entregas do TP2 e TP3](#3-entregas-do-tp2-e-tp3)
4. [TP4: API com modelo de linguagem local](#4-tp4-api-com-modelo-de-linguagem-local)
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
| Modelagem / Modeling | Sem modelo preditivo (o charter exclui previsão). Cálculo das participações e comparações; no TP4, o LLM de resumo em `Code/modeling/` |
| Avaliação / Customer Acceptance | Página *Fontes e método* confere os critérios de sucesso; o avaliador acadêmico exerce o papel do cliente |
| Implantação / Deployment | Painel (`Scripts/app.py`), API (`Code/api/main.py`), notas em `Code/deployment/` |

Papéis: líder (escopo, charter); Data Scientist/Engineer (fontes, indicadores); Solution
Architect (estrutura TDSP, ambiente, arquitetura).

## 3. Entregas do TP2 e TP3

Painel Streamlit multipágina: `Scripts/app.py` (Início) e `Scripts/pages/` (ver `Scripts/README.md` e `Scripts/pages/README.md`). Com a API no ar,
as páginas a consomem e indicam a origem do dado ("API FastAPI" ou "leitura direta"); sem
ela, o painel lê as fontes diretamente.

| Item | Onde / como |
|---|---|
| Ambiente e deploy | `requirements.txt` com versões fixas; `.gitignore` (`.venv/`, `.env`, segredos); Git na `main`; deploy no Streamlit Community Cloud (entrada `Scripts/app.py`; ver `Code/deployment/README.md`) |
| Interface | 6 páginas em 3 seções: Panorama setorial, Série histórica (seletor de anos), Comparação internacional (upload CSV), Corpus e resumos (meta, nuvem de palavras, aba Corpus e aba Resumo com o modelo local), Fontes e método |
| API FastAPI | `Code/api/main.py`, routers (ver `Code/api/routers/README.md`) e modelos Pydantic; GET de saúde, série, World Bank, metas ODS 9 e fatos/resumo; `POST /world-bank` (201). Cliente em `Scripts/cliente_api.py` |
| Web scraping | `Code/data_acquisition/scrape_ods9.py` (Beautiful Soup, sem Selenium: nenhuma fonte é dinâmica) grava `Data/raw/ods9_metas.csv` e `ods9_corpus.txt` (ver `Code/data_acquisition/README.md`) |
| Cache e sessão | `st.cache_data` (1 h nas consultas SIDRA/Ipeadata e nas respostas da API); CSV enviado em `st.session_state` |
| Upload e download | `st.file_uploader` (CSV do DataBank → `POST /world-bank`); downloads de exemplo, recorte filtrado, tabelas SIDRA/Ipeadata (com fonte, código e data), TXT do Ipea e corpus |
| Documentação | `Docs/Project_Charter.md`, `Docs/Data_Summary_Report.md`, READMEs por pasta |

## 4. TP4: API com modelo de linguagem local

A rota **`POST /processar_texto`** resume um texto (50 a 2.000 caracteres) com o
**[`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B)** (Apache 2.0, sem conta), executado na máquina do usuário, em float32 na
CPU, sem internet após o download. Na página *Corpus e resumos*, a aba **Resumo** usa essa rota
para resumir uma meta do ODS 9, um resumo de referência ou a introdução de Oreiro e Feijó (2010), em português.

**Integração com o LLM.** `Code/modeling/resumidor.py` carrega o modelo uma vez,
na subida da API, e gera o resumo; `Code/api/routers/texto.py` expõe a rota. O painel a
consome pelo `Scripts/cliente_api.py`. Medição (`Code/modeling/medir_modelo.py`, ver `Code/modeling/README.md`), no banco
de 10 textos: 12–38 s por resumo (mediana 26 s), ~2,4 GB de RAM.

**Integração local (passos, bibliotecas, hardware).**
- Bibliotecas: `transformers` (tokenizador e geração), `torch` (só CPU, via `--extra-index-url`
  no `requirements.txt`), `huggingface_hub` (download único), `fastapi` e `uvicorn`; `psutil` e
  `httpx` só em medição e testes.
- Passos: seção 5 (instalar → baixar o modelo → subir a API). Com o modelo em disco, funciona
  offline (`HF_HUB_OFFLINE=1`).
- Ajustes ao hardware (Intel Core i5-1035G1, 8 GB de RAM, sem GPU): float32 na CPU (~2,4 GB de
  RAM); modo de raciocínio do Qwen3 desligado (`enable_thinking=False`), pois o resumo só
  precisa da resposta; aviso de links simbólicos do cache Hugging Face no Windows é inofensivo
  (só ocupa mais disco). O Qwen2.5-1.5B-Instruct (~6,2 GB só de pesos) travou a máquina e foi
  descartado.
- Detalhes: `Code/api/README.md` e `Docs/Escolha_do_modelo.md` (seção 4).

**Response Models.** Todas as rotas declaram `response_model` com modelos
Pydantic em `Code/api/models.py`; os pedidos rejeitam campos extras. A rota de texto devolve o
resumo em formato estruturado e documentado em `/docs`.

**Tratamento de erros.** Exceções HTTP específicas por cenário
(`Code/api/erros.py`, `Code/api/routers/texto.py`), declaradas no `/docs` e cobertas por
testes com modelo falso (`Code/api/tests/`, ver `Code/api/tests/README.md`):

| Código | Cenário |
|---|---|
| 422 | texto com menos de 50 ou mais de 2.000 caracteres, campo extra ou tipo de análise inválido |
| 502 | o modelo devolveu resumo vazio |
| 503 | o modelo não carregou na subida (as demais rotas seguem no ar) |
| 504 | geração acima de 120 s |
| 500 | erro inesperado: mensagem com código de rastreio; o traceback fica só no log |

**Escolha do modelo.** Critérios: desempenho (qualidade do resumo em português),
custo computacional (cabe em 8 GB de RAM sem GPU, tempo por resumo aceitável) e
acessibilidade (licença aberta, sem conta, ~1,5 GB). O Qwen2.5-1.5B foi descartado antes da medição, porque travou a máquina sem terminar o
primeiro texto. Os outros dois foram medidos num banco de 10 textos (7 justificativas do
ODS 9 e 3 resumos de referência; saídas em `Data/modeled/`, ver `Data/modeled/README.md`): o Qwen2.5-0.5B-Instruct e o
Qwen3-0.6B. O Qwen3-0.6B foi escolhido, porque errou menos nos textos do tema, e não por
ser o mais rápido ou o mais leve. Justificativa completa, medições e erros encontrados em
`Docs/Escolha_do_modelo.md`, que também registra o uso de IA.

**Limites:** o resumo é gerado por modelo e exige revisão humana antes de ser usado como fato;
textos em inglês podem gerar resumos que repetem o título. O **Streamlit Cloud não roda o
modelo**: a aplicação publicada lê as fontes direto, sem a API; a rota de texto só existe com a
API local.

### 4.1 Observações do TP3 tratadas no TP4

- **`cliente_api.py` com fallback e indicação da origem:** feito, com uma diferença. A função nova `analisar_texto` não tem fallback como as demais: sem a API, a aba Resumo mostra "indisponível" e não indica a origem do dado.
- **Scraping do ODS 9 igual ao do TP2:** tratado. O projeto ganhou uma fonte e um script novos: o scraping das referências sobre desindustrialização (`Code/data_acquisition/scrape_referencias.py`).

### 4.2 Onde verificar cada critério

| Critério | Onde está | Como verificar |
|---|---|---|
| Integração funcional com o LLM | `Code/modeling/resumidor.py`, `Code/api/routers/texto.py` | Subir o projeto (seção 5) e abrir http://127.0.0.1:8000/docs: testar `POST /processar_texto`. Ou, no painel (http://localhost:8501), aba **Resumo** em *Corpus e resumos* |
| Descrição detalhada da integração (ambiente, bibliotecas, hardware) | Esta seção 4, `Code/api/README.md`, `Docs/Escolha_do_modelo.md` (seção 4) | Ler as três; as bibliotecas estão em `requirements.txt` |
| Response Models | `Code/api/models.py` (`PedidoTexto`, `ResultadoResumo`) | Em /docs, ver os esquemas; enviar um texto com campo extra e conferir o 422 |
| Tratamento de erros | `Code/api/erros.py`, `Code/api/routers/texto.py`, `Code/api/tests/` | `.venv\Scripts\python.exe -m unittest discover -s Code\api\tests -t .` (cobre 422, 502, 503, 504 e 500) |
| Justificativa da escolha do modelo | `Docs/Escolha_do_modelo.md` (seções 2 e 3) | Ler a tabela de candidatos e a seção de justificativas; as medições estão em `Data/modeled/` |

## 5. Como rodar (Windows)

Na pasta do projeto, nesta ordem (passos 1 a 3 obrigatórios; o 4 mostra o painel). Os
comandos chamam o Python do `.venv` direto, então não é preciso ativar o ambiente.

1. **Ambiente e dependências** (uma vez):
   Use Python 3.12, 3.13 ou 3.14 (testado com 3.13). O Python 3.15 não serve: o pandas 3.0.5 não tem pacote pronto para ele.
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
2. **Baixar o modelo** (uma vez, com internet, ~1,5 GB; sem isto a rota de texto responde 503):
   ```
   .venv\Scripts\python.exe Code\modeling\baixar_modelo.py
   ```
3. **Subir a API** (terminal aberto; docs em http://127.0.0.1:8000/docs). Com `--reload`, cada
   arquivo salvo recarrega o modelo; para uso contínuo, rode sem ele:
   ```
   .venv\Scripts\python.exe -m uvicorn Code.api.main:app --reload
   ```
4. **Subir o painel** (outro terminal). O painel abre em http://localhost:8501:
   ```
   .venv\Scripts\python.exe -m streamlit run Scripts/app.py
   ```

**Forma rápida (opcional).** O comando abaixo faz os passos 1 a 4 de uma vez: cria o
ambiente e instala as dependências se ainda não existirem, confere o modelo, sobe a API em
outra janela e sobe o painel nesta, em http://localhost:8501. Para parar, feche as duas janelas.

```
python iniciar.py
```

Os passos acima continuam valendo para quem quiser controlar cada etapa.

**Opcional — regerar os dados extraídos** (já estão em `Data/raw/`, ver `Data/raw/README.md`):
```
.venv\Scripts\python.exe Code\data_acquisition\scrape_ods9.py
.venv\Scripts\python.exe Code\data_acquisition\scrape_referencias.py
```

**Testes** (da raiz do projeto):

```
.venv\Scripts\python.exe -m unittest discover -s Code\api\tests -t .
```

Teste com o modelo real (demora cerca de 1 minuto):

```
set RODAR_MODELO_REAL=1
.venv\Scripts\python.exe -m unittest Code.api.tests.test_modelo_real -v
```

Sem a API, o painel mostra "Origem: leitura direta" e segue funcionando; só a aba Resumo
exige a API. Exemplos de chamadas e testes: `Code/api/README.md`.

## 6. Estrutura de diretórios

Cada pasta de código e de dados tem um README próprio.

```
Docs/                 # Project_Charter, Data_Summary_Report, Referencias, Escolha_do_modelo
Data/
    raw/              # dados brutos (inclui referências para o teste do modelo)
    processed/        # envios do POST /world-bank
    modeled/          # resumos gerados nas medições do modelo
Code/
    api/              # FastAPI: main, models, erros, routers/, tests/
    data_acquisition/ # scraping (ODS 9 e referências)
    data_exploration/ # entendimento e EDA (reservada)
    modeling/         # resumidor, baixar_modelo, medir_modelo
    deployment/       # notas de implantação
Scripts/              # app.py, nucleo.py, dados.py, cliente_api.py, interface.py, pages/, assets/
requirements.txt
.gitignore
README.MD
```
