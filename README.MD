# Monitor Brasileiro de Desindustrialização

Dashboard (em construção) para acompanhar a participação da indústria no
PIB brasileiro, alinhado ao ODS 9.2 e ao pilar Social do ESG.

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
fontes oficiais.

Metas e indicadores de sucesso: montar a série histórica da participação de
agropecuária, indústria e serviços no PIB, no maior período disponível, com a
indústria aberta em subsetores quando a fonte permitir. O projeto é
bem-sucedido se a série do indicador 9.2.1 tiver valor em mais de 90% dos anos
a partir de 1995 (percentual exibido no painel); se cada tabela baixada
indicar fonte, código da série e data de extração; se a soma setorial for
coerente com o valor adicionado a preços básicos, e não com 100% do PIB a
preços de mercado; se os dados do IBGE forem compatíveis com o Ipeadata e com
a literatura; se as quebras metodológicas estiverem sinalizadas no painel; e
se a aplicação exibir sempre a divulgação oficial mais recente, sem valores
inseridos manualmente.

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
CRISP-DM organiza o trabalho em seis fases; o TDSP, da Microsoft, acrescenta
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
    Padronização das séries e cálculo das participações em Scripts/dados.py,
    com os dados brutos em Data/raw/ e os limpos em Data/processed/, quando
    houver arquivo intermediário. Cada ponto conserva fonte, código da série e
    data de extração.

Modelagem:
    Não há modelo preditivo, porque o charter exclui previsão. A fase
    corresponde ao cálculo dos indicadores de participação e às comparações
    setorial e internacional, com destino em Code/modeling/ e Data/modeled/.

Avaliação:
    Verificação da cobertura da série, da procedência de cada valor, da
    coerência da soma setorial e da compatibilidade entre IBGE, Ipeadata e
    literatura, conforme as metas da seção 1.

Implantação:
    Painel Streamlit em Scripts/app.py, com notas em Code/deployment/.

- TDSP:

Business Understanding:
    Docs/Project_Charter.md define problema, escopo, objetivos, critérios de
    sucesso e interessados.

Data Acquisition and Understanding:
    Três formas de aquisição: API no painel (Scripts/dados.py), scraping em
    script separado (Code/data_acquisition/scrape_ods9.py) e arquivo do
    DataBank enviado pelo usuário na página Comparação internacional.

Modeling:
    Produção dos indicadores de participação no PIB e das comparações, em
    ciclo com a aquisição quando a qualidade dos dados não for suficiente.

Deployment:
    Painel Streamlit, ambiente Python em requirements.txt e organização das
    pastas, documentados em Code/deployment/.

Customer Acceptance:
    Confronto da entrega com as metas da seção 1 e com o público descrito no
    charter. No contexto acadêmico, o avaliador exerce esse papel.

Papéis no eixo vertical:
    Líder do projeto: escopo, charter e critérios de sucesso. Data Scientist e
    Data Engineer: fontes, extração, qualidade dos dados e indicadores.
    Solution Architect: estrutura TDSP, ambiente de execução e arquitetura do
    Streamlit.

# 3. Funcionalidades entregues nesta etapa

A aplicação é um painel Streamlit com múltiplas páginas: Scripts/app.py é o
ponto de entrada (página Início) e as demais páginas estão em Scripts/pages/.
A relação a seguir indica onde cada entrega desta etapa se encontra no
repositório.

Ambiente e organização:
    O arquivo requirements.txt fixa as versões das dependências; o .gitignore
    exclui .venv/, __pycache__/ e .streamlit/secrets.toml; as notas de
    implantação estão em Code/deployment/. A estrutura de pastas segue o TDSP,
    descrita na seção 4.

Interface interativa:
    São cinco páginas no menu lateral. Panorama setorial utiliza abas
    (trimestral e subsetores); Série histórica dispõe de seletor de intervalo
    de anos; Comparação internacional dispõe de seleção múltipla de países e de
    indicadores, seletor de período, escolha do tipo de gráfico (evolução,
    comparação em um ano e composição setorial) e da transformação dos valores
    (valor original, índice 100 e variação em pontos percentuais); Contexto
    ODS 9 dispõe de seleção da meta e do escopo da nuvem de palavras.

Extração de conteúdo da web com Beautiful Soup:
    O script Code/data_acquisition/scrape_ods9.py é executado separadamente da
    aplicação e grava Data/raw/ods9_metas.csv (uma linha por meta, com fonte e
    data de extração) e Data/raw/ods9_corpus.txt (texto concatenado das metas).

Exibição do conteúdo extraído:
    A página Contexto ODS 9 apresenta o texto da meta selecionada, a nuvem de
    palavras e a frequência de palavras em gráfico de barras. As estatísticas
    das séries (participação no último ano, variação desde 1995 e completude do
    recorte) são apresentadas na página Início e na Série histórica.

Cache e estado de sessão:
    As funções de carga em Scripts/dados.py utilizam st.cache_data, com tempo
    de expiração de uma hora nas consultas de API. O arquivo CSV enviado pelo
    usuário é mantido em st.session_state na página Comparação internacional e
    permanece disponível durante a navegação entre as páginas, juntamente com
    os filtros selecionados.

Serviço de upload e download de arquivos:
    O componente st.file_uploader, na página Comparação internacional, recebe o
    CSV do DataBank, que passa a alimentar os filtros, os gráficos e a tabela.
    Para download, a aplicação disponibiliza o CSV de exemplo, o recorte
    filtrado, as tabelas do SIDRA e do Ipeadata (com fonte, código da série e
    data de extração anexados) e o arquivo TXT do texto extraído do Ipea.

Documentação do projeto:
    Docs/Project_Charter.md apresenta escopo, objetivos, entregas, stakeholders
    e riscos; Docs/Data_Summary_Report.md apresenta a hierarquia das fontes, as
    ressalvas de método e a ficha de cada fonte com o respectivo objetivo de
    uso.

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
        processed/             # dados limpos / preparados
        modeled/               # saídas de modelagem
    Code/
        data_acquisition/      # extração via API (quando houver script à parte)
        data_exploration/      # entendimento e EDA
        modeling/              # modelos
        deployment/            # empacotamento / notas de implantação
    Scripts/
        app.py                 # visão geral do dashboard Streamlit
        dados.py               # carga, transformação e corpus
        interface.py           # avisos, métrica e download
        pages/                 # páginas do painel
    requirements.txt
    README.MD
```

# 5. Como rodar a aplicação (Windows) em ordem:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python Code/data_acquisition/scrape_ods9.py
streamlit run Scripts/app.py
```
