# Monitor Brasileiro de Desindustrialização

Painel para acompanhar a participação da indústria no PIB brasileiro,
alinhado ao ODS 9.2 e ao pilar Social do ESG.

Aplicação publicada: [(Streamlit)](https://projetointeligenciaartificialaplicada-bahhxlugo9rejaxkrd3njj.streamlit.app/)

Este README foi redigido com apoio de inteligência artificial (Claude Opus 5.5) e revisado pelo autor do projeto.

# 1. Identificação do problema de negócio

Problema de negócio: o Brasil perde participação da indústria de
transformação no produto interno há décadas, movimento registrado nas Contas
Nacionais do IBGE e tratado na literatura como desindustrialização (Tregenna,
2009; Oreiro e Feijó, 2010; Morceiro, 2021; citações em Docs/Referencias.md).
O efeito é o avanço de ocupações em serviços de baixa produtividade, com menos
empregos formais, e a perda de capacidade de inovar e de exportar bens mais
sofisticados. A evidência oficial existe, porém permanece dispersa entre bases
estatísticas e relatórios especializados. O problema que a aplicação resolve é
a falta de um painel acessível que reúna essa trajetória setorial a partir de
fontes oficiais. Nesta etapa o painel também expõe as mesmas séries e textos
por uma API FastAPI local, preparando a consulta em linguagem natural na
etapa de LLM.

Metas e indicadores de sucesso: comparar a participação de agropecuária,
indústria e serviços no PIB, com a indústria aberta em subsetores quando a
fonte permitir, e montar a série histórica da indústria de transformação no
maior período disponível. O projeto é
bem-sucedido se a série do indicador 9.2.1 tiver valor em mais de 90% dos anos
a partir de 1995 (percentual exibido no painel); se cada tabela baixada
indicar fonte, código da série e data de extração; se a soma setorial for
coerente com o valor adicionado a preços básicos, e não com 100% do PIB a
preços de mercado; se os dados do IBGE forem compatíveis com o Ipeadata e com
a literatura; se as quebras metodológicas estiverem sinalizadas no painel;
se as séries consultadas por API exibirem sempre a divulgação oficial mais
recente, sem valores inseridos manualmente; e se as rotas da API FastAPI
estiverem descritas em /docs.

Pilar ESG: o projeto se insere no pilar Social (S), porque a retração da
indústria de transformação reduz a oferta relativa de empregos formais e de
maior produtividade. Complementarmente, dialoga com o pilar Ambiental (E),
pela industrialização inclusiva e sustentável da meta 9.2, e com o pilar
Governança (G), pelo uso de dados públicos no debate de política industrial.

ODS atendida e justificativa: o projeto atende ao ODS 9 (Indústria, Inovação e
Infraestrutura), na meta 9.2. O indicador oficial 9.2.1 é o valor adicionado
da indústria de transformação como proporção do PIB e per capita; este projeto
cobre o componente em proporção do PIB. O ODS 8 (Trabalho Decente e
Crescimento Econômico) entra apenas como contexto.

Precisão do recorte: o indicador medido é a indústria de transformação (código
90693 no SIDRA), e não o agregado "indústria" (90691), que inclui extrativa,
construção e utilities. As séries estão a preços correntes, de modo que a
participação também se move por preço relativo. As ressalvas de método estão
detalhadas em Docs/Data_Summary_Report.md.

Divergência entre ONU e Brasil: a redação da ONU para a meta 9.2 pede aumentar
a participação da indústria no PIB e no emprego, enquanto a redação adaptada
pelo Ipea desloca o foco para produtividade e complexidade tecnológica. O
painel assume essa divergência: as séries medem o indicador da ONU e o texto
extraído da página do Ipea entra como ressalva oficial brasileira.

Público-alvo: formuladores de políticas públicas de desenvolvimento econômico
e industrial, entidades de classe e federações industriais, pesquisadores e
estudantes de economia, áreas de ESG e relações institucionais, além de
demais interessados no tema.

# 2. Organização do projeto (CRISP-DM e TDSP)

O projeto é estruturado pelos métodos CRISP-DM e TDSP, usados em conjunto. O
CRISP-DM organiza o trabalho em seis fases; o TDSP acrescenta
papéis de equipe e a estrutura de pastas adotada em Docs/, Data/, Code/ e
Scripts/. As listas a seguir indicam o artefato correspondente a cada fase.

- CRISP-DM:

Entendimento do negócio:
    Seção 1 deste README e Docs/Project_Charter.md, que delimita o que entra e
    o que não entra no escopo.

Entendimento dos dados:
    Docs/Data_Summary_Report.md e Code/data_exploration/. As fontes desta
    etapa são IBGE/SIDRA (tabela 1846), Ipeadata, World Bank (NV.IND.MANF.ZS)
    e a página ODS 9 do Ipea.

Preparação dos dados:
    Padronização das séries e cálculo das participações em Scripts/nucleo.py
    (o painel envolve essas funções com cache em Scripts/dados.py), com os
    dados brutos em Data/raw/ e os recebidos por POST em Data/processed/.
    Cada ponto conserva fonte, código da série e data de extração.

Modelagem:
    Não há modelo preditivo, porque o charter exclui previsão. A fase
    corresponde ao cálculo dos indicadores de participação e às comparações
    setorial e internacional, com destino em Code/modeling/ e Data/modeled/.

Avaliação:
    Verificação da cobertura da série, da procedência de cada valor, da
    coerência da soma setorial e da compatibilidade entre IBGE, Ipeadata e
    literatura, conforme as metas da seção 1. A página Fontes e método
    calcula esses critérios e os exibe como atendidos ou não.

Implantação:
    Painel Streamlit em Scripts/app.py e API FastAPI em Code/api/main.py,
    com notas em Code/deployment/. A fase de Avaliação aparece na página
    Fontes e método, que verifica os critérios de sucesso do charter.

- TDSP:

Business Understanding:
    Docs/Project_Charter.md define problema, escopo, objetivos, critérios de
    sucesso e interessados.

Data Acquisition and Understanding:
    Três formas de aquisição das fontes oficiais: API (SIDRA e Ipeadata, em
    Scripts/nucleo.py), scraping em script separado
    (Code/data_acquisition/scrape_ods9.py) e arquivo do DataBank enviado pelo
    usuário na página Comparação internacional. A API FastAPI do projeto
    consulta as mesmas fontes; Início, Série histórica, Comparação
    internacional e Contexto ODS 9 consomem essas rotas, com leitura
    direta se o serviço não responder. O POST /world-bank grava o CSV
    enviado pelo usuário em Data/processed/world_bank_envios/.

Modeling:
    Produção dos indicadores de participação no PIB e das comparações, em
    ciclo com a aquisição quando a qualidade dos dados não for suficiente.

Deployment:
    Painel Streamlit, API FastAPI local, ambiente Python em requirements.txt
    e organização das pastas, documentados em Code/deployment/.

Customer Acceptance:
    Confronto da entrega com as metas da seção 1 e com o público descrito no
    charter. No contexto acadêmico, o avaliador exerce esse papel.

Papéis no eixo vertical:
    Líder do projeto: escopo, charter e critérios de sucesso. Data Scientist e
    Data Engineer: fontes, extração, qualidade dos dados e indicadores.
    Solution Architect: estrutura TDSP, ambiente de execução e arquitetura do
    Streamlit.

# 3. Funcionalidades entregues nesta etapa

Nesta etapa o painel passou a expor os dados por uma API FastAPI local.
Antes, Início, Série histórica e Contexto ODS 9 liam SIDRA, Ipeadata e os
arquivos em Data/raw/ direto; a Comparação internacional lia o CSV do
DataBank no próprio Streamlit. Agora essas páginas consultam a FastAPI
quando ela está no ar (GET /fatos/resumo, GET /serie/transformacao,
GET /ods9/metas). O CSV da Comparação internacional continua a ser
enviado pelo usuário; a mudança é o caminho: POST /world-bank recebe o
arquivo, a API o valida e grava, e GET /world-bank/{id} devolve os dados
para os gráficos. Se a API não responder, o painel volta à leitura
direta.

A aplicação é um painel Streamlit com múltiplas páginas: Scripts/app.py é o
ponto de entrada (página Início) e as demais páginas estão em Scripts/pages/.
O menu lateral agrupa as páginas em Painel, Comparações e contexto, e Método.
A relação a seguir indica onde cada entrega desta etapa se encontra no
repositório.

Ambiente e organização:
    O arquivo requirements.txt fixa as versões das dependências; o .gitignore
    exclui `.venv/`, `__pycache__/`, `.env` e `.streamlit/secrets.toml`; as
    notas de implantação estão em Code/deployment/. A estrutura de pastas
    segue o TDSP, descrita na seção 4.

Controle de versão e preparação para deploy:
    O projeto é versionado com Git, na branch main, e publicado no
    Streamlit Community Cloud a partir deste repositório (link no início
    deste README). O ambiente de execução é reprodutível a partir de
    requirements.txt em uma virtualenv, conforme a seção 5, e o ponto de
    entrada do deploy é Scripts/app.py, descrito em
    Code/deployment/README.md. A API FastAPI roda só em ambiente local.

Interface interativa:
    O menu tem seis páginas em três seções. Panorama setorial usa o acumulado
    dos últimos quatro trimestres, mostra agropecuária, indústria, serviços e
    impostos (que somam o PIB) e isola a transformação como "dos quais";
    Série histórica dispõe de seletor de intervalo de anos e consome
    GET /serie/transformacao; Comparação internacional recebe o CSV do
    DataBank pelo upload (POST /world-bank e GET /world-bank/{id} quando a
    API está no ar); Contexto ODS 9 dispõe de seleção da meta, nuvem de
    palavras e aba Corpus; Fontes e método resume as fontes e o status da
    API local. Início, Série histórica, Comparação internacional e Contexto
    ODS 9 indicam a origem do dado (API FastAPI ou leitura direta).

API FastAPI:
    Code/api/main.py reúne routers em Code/api/routers/ e modelos Pydantic
    em Code/api/models.py (response_model em todas as rotas; POST /world-bank
    devolve 201). A consulta de dados é GET (saúde, série de transformação,
    World Bank por id, metas do ODS 9 e fatos/resumo). O envio de novos
    dados é POST /world-bank: recebe o CSV do DataBank que a Comparação
    internacional usa nos gráficos. As rotas estão descritas em
    Code/api/README.md e em /docs. O cliente está em Scripts/cliente_api.py.

Extração de conteúdo da web com Beautiful Soup:
    O script Code/data_acquisition/scrape_ods9.py é executado separadamente da
    aplicação e grava Data/raw/ods9_metas.csv e Data/raw/ods9_corpus.txt.
    Nesta etapa esses dados foram aprimorados: as metas do ODS 9 passaram a
    ser servidas pela API (GET /ods9/metas e GET /ods9/metas/{codigo}),
    reunidas na aba Corpus e preparadas como base de Q&A e resumo para a
    etapa de LLM. Como nenhuma fonte exige interação dinâmica, a coleta
    seguiu a orientação de manter a simplicidade, sem Selenium; a
    justificativa está em Docs/Data_Summary_Report.md.

Exibição do conteúdo extraído:
    A página Contexto ODS 9 apresenta o texto da meta selecionada, a nuvem de
    palavras, a frequência e, na aba Corpus, as metas extraídas. As
    estatísticas das séries vêm de GET /fatos/resumo na
    página Início.

Cache e estado de sessão:
    As funções de carga em Scripts/dados.py utilizam st.cache_data, com tempo
    de expiração de uma hora nas consultas de SIDRA e Ipeadata, envolvendo
    Scripts/nucleo.py. As respostas da API FastAPI também entram em cache.
    O arquivo CSV enviado pelo usuário é mantido em st.session_state na página
    Comparação internacional.

Serviço de upload e download de arquivos:
    O componente st.file_uploader, na página Comparação internacional, recebe o
    CSV do DataBank. Com a API no ar, o arquivo vai para POST /world-bank e
    os dados voltam de GET /world-bank/{id}; sem ela, o painel lê o CSV
    direto. Em ambos os casos o envio alimenta filtros, gráficos e tabela.
    Para download, a aplicação disponibiliza o CSV de exemplo, o recorte
    filtrado, as tabelas do SIDRA e do Ipeadata (com fonte, código da série e
    data de extração anexados), o arquivo TXT do texto extraído do Ipea e o
    recorte do corpus na aba Corpus.

Documentação do projeto:
    Docs/Project_Charter.md apresenta escopo, objetivos, entregas, preparação
    para IA, stakeholders e riscos; Docs/Data_Summary_Report.md apresenta a
    hierarquia das fontes, as ressalvas de método, a decisão sobre Selenium e
    a ficha de cada fonte com o respectivo objetivo de uso.

# 4. Estrutura de diretórios

A árvore abaixo segue as fases do TDSP. Cada pasta de código e de dados possui
um README próprio, que descreve o conteúdo nela armazenado.

```
monitor-desindustrializacao/
    Docs/                      # Business Understanding e relatórios
        Project_Charter.md
        Data_Summary_Report.md
        Referencias.md
    Data/
        raw/                   # dados brutos
        processed/             # POST /world-bank (envios do DataBank)
        modeled/               # saídas de modelagem
    Code/
        api/                   # FastAPI local (main, models, routers)
        data_acquisition/      # extração fora do app (scraping do ODS 9)
        data_exploration/      # entendimento e EDA
        modeling/              # modelos
        deployment/            # empacotamento / notas de implantação
    Scripts/
        app.py                 # visão geral do dashboard Streamlit
        nucleo.py              # carga e transformação (sem Streamlit)
        dados.py               # cache Streamlit sobre nucleo.py
        cliente_api.py         # GET/POST na FastAPI com fallback
        interface.py           # avisos, métrica, gráficos e download
        assets/                # ícone do ODS 9
        pages/                 # páginas do painel
    requirements.txt
    .gitignore                 # ambiente virtual, cache e segredos
    README.MD
```
### OBS: As pastas de exploração e modelagem seguem reservadas para as próximas etapas; o tratamento das séries ocorre em Scripts/nucleo.py. Data/processed/ guarda os arquivos recebidos pela API.

# 5. Como rodar a aplicação (Windows) em ordem:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python Code/data_acquisition/scrape_ods9.py
uvicorn Code.api.main:app --reload
```

Em outro terminal, com o mesmo ambiente virtual:

```
streamlit run Scripts/app.py
```

A API fica em http://127.0.0.1:8000 e a documentação interativa em
http://127.0.0.1:8000/docs. Com a API no ar, Início, Série histórica,
Comparação internacional e Contexto ODS 9 mostram "Origem: API FastAPI".
Sem ela, mostram "Origem: leitura direta" e continuam funcionando. A
página Fontes e método indica quando o serviço está fora. Exemplos de
curl estão em Code/api/README.md.
