# Monitor Brasileiro de Desindustrialização

Dashboard (em construção) para acompanhar a participação da indústria no
PIB brasileiro, alinhado ao ODS 9.2 e ao pilar Social do ESG.

# 1. Identificação do problema de negócio

Problema de negócio: o Brasil enfrenta um processo prolongado de perda de relevância relativa da indústria de transformação no produto interno, registrado nas Contas Nacionais do IBGE e tratado na literatura como desindustrialização: queda sustentada da participação da manufatura no PIB e no emprego (Tregenna, 2009). No Brasil, Oreiro e Feijó (2010) e Morceiro (2021) situam esse movimento no recorte a preços correntes e nas quebras metodológicas das Contas Nacionais; o debate sobre desindustrialização prematura está em Palma (2005) e Rodrik (2016). Citações completas em Docs/Referencias.md. A evidência governamental existe, porém permanece dispersa em bases estatísticas e em relatórios especializados. A desindustrialização resulta em serviços de baixa produtividade; menos postos mais formais e estáveis de trabalho, enquanto avançam ocupações em serviços, inclusive informais; e reduz capacidade de inovar, gerar superávit em setores mais sofisticados e sustentar uma inserção internacional mais complexa. O problema que a aplicação resolve é a falta de um painel acessível que reúna essa trajetória setorial e torne visível a desindustrialização brasileira a partir de fontes oficiais.

Metas e indicadores de sucesso: usar as fontes oficiais para montar uma série histórica da participação de agropecuária, indústria e serviços no PIB brasileiro, no maior período disponível. Quando a fonte permitir, a indústria será separada em transformação, extrativa, construção civil e eletricidade, água e gás. O projeto será bem-sucedido se a série do indicador 9.2.1 tiver valor em mais de 90% dos anos a partir de 1995 (percentual exibido no painel para o recorte escolhido); se cada tabela baixada indicar fonte, código da série e data de extração; se a soma agropecuária + indústria + serviços for coerente com o valor adicionado a preços básicos, e não com 100% do PIB a preços de mercado (a diferença são os impostos líquidos sobre produtos); se os dados do IBGE forem compatíveis com o Ipeadata e com um valor publicado na literatura (Data Summary Report, Fonte 3); se as mudanças de metodologia das Contas Nacionais estiverem identificadas no painel; e se a aplicação exibir a divulgação oficial mais recente, sem valores inseridos manualmente; no caso do World Bank, cuja extração é por arquivo, exibindo a data de atualização registrada no próprio export.

Pilar ESG: o projeto se insere principalmente no pilar Social (S), porque a retração da indústria de transformação reduz a oferta relativa de empregos formais e de maior produtividade. Esse vínculo justifica o recorte. Complementarmente, dialoga com o pilar Ambiental (E) (industrialização inclusiva e sustentável da meta 9.2) e com o pilar Governança (G) (uso de dados públicos e transparentes para o debate de política industrial). O que o painel não exibe nesta etapa (emprego, per capita, volume) está no escopo do Project Charter.

ODS atendida e justificativa: o projeto atende primariamente ao ODS 9 (Indústria, Inovação e Infraestrutura), especificamente à meta 9.2. O indicador oficial 9.2.1 é o "valor adicionado da indústria de transformação como proporção do PIB e per capita"; o núcleo de dados deste projeto é o componente em proporção do PIB. Secundariamente, o projeto se relaciona ao ODS 8 (Trabalho Decente e Crescimento Econômico) só como contexto. O indicador 9.2.2 é o caminho previsto para sustentar o pilar Social com dado, em etapa posterior.

Precisão do recorte: o indicador medido é o 9.2.1 da ONU, isto é, a indústria de transformação. No SIDRA, "indústria" (código 90691) é o agregado, que inclui extrativa, construção e eletricidade/gás/água; transformação é o código 90693. Os dois não contam a mesma história, porque o agregado pode se sustentar por extrativa ou construção enquanto a manufatura recua. As séries do SIDRA e do Ipeadata estão a preços correntes, de modo que a participação no PIB também se move por preço relativo, e não apenas por volume produzido (Oreiro e Feijó, 2010; Morceiro, 2021). A participação em volume fica para etapa posterior.

Divergência entre ONU e Brasil: a redação da ONU para a meta 9.2 pede aumentar a participação da indústria no PIB e no emprego. A redação adaptada pelo Ipea trocou esse foco por produtividade e complexidade tecnológica, com o argumento de que o baixo dinamismo da economia brasileira não decorre da mudança estrutural entre indústria e serviços. O painel assume essa divergência: as séries medem o indicador da ONU e o texto extraído da página do Ipea entra como ressalva oficial brasileira, não como o que os gráficos demonstram.

Público-alvo: formuladores de políticas públicas em áreas de desenvolvimento econômico e industrial, entidades de classe e federações industriais, pesquisadores e estudantes de economia, áreas de ESG/relações institucionais de empresas e interessados no tema (público).

# 2. Organização do projeto (CRISP-DM e TDSP)

O projeto é estruturado pelos métodos CRISP-DM e TDSP, usados em conjunto. O CRISP-DM organiza o trabalho de dados em seis fases sequenciais. O TDSP, da Microsoft, descreve o ciclo de vida de um projeto de ciência de dados com fases, papéis de equipe e uma estrutura de pastas. As pastas Docs/, Data/, Code/ e Scripts/ seguem o TDSP; o conteúdo de cada fase está descrito abaixo.

- CRISP-DM: O método tem seis fases. Cada uma se aplica a este painel da seguinte forma.

Entendimento do negócio:
    Define o problema, o recorte, as metas e o público. Neste projeto, essa fase corresponde à seção 1 deste README e a Docs/Project_Charter.md: tornar visível a participação da indústria no PIB brasileiro, alinhada ao ODS 9 e ao pilar Social do ESG. O charter delimita o que entra (série nacional de agropecuária, indústria e serviços; subsetores industriais quando a fonte permitir; comparação internacional) e o que não entra (microdados, recorte estadual, emprego como série principal, avaliação causal de política e previsão da desindustrialização).

Entendimento dos dados:
    Identifica fontes, tipos e uso. Neste projeto, a fase está em Docs/Data_Summary_Report.md e em Code/data_exploration/. As fontes desta etapa são IBGE/SIDRA (Contas Nacionais trimestrais e subsetores da tabela 1846), Ipeadata, World Bank (indicador NV.IND.MANF.ZS) e a página ODS 9 do Ipea. Banco Central (SGS) e demais estudos estão nas fontes previstas do Data Summary Report. O objetivo desta fase é conhecer o contrato de cada extração, a periodicidade e os riscos de qualidade, como campos vazios no SIDRA e mudanças de metodologia das Contas Nacionais.

Preparação dos dados:
    Limpa, padroniza e calcula as participações setoriais a partir das extrações. Neste projeto, os dados brutos entram em Data/raw/ e os dados limpos em Data/processed/, quando houver arquivo intermediário. A fase inclui unificar datas e unidades, tratar valores inválidos, calcular a participação de cada setor no PIB e registrar a origem de cada ponto (fonte, código da série, unidade e data de extração), conforme as metas da seção 1. O dashboard consulta SIDRA e Ipeadata por API, com cache no Streamlit. O World Bank entra por CSV: o arquivo fica em Data/raw/ como exemplo; o painel só o usa depois do upload na página Comparação internacional. O tratamento é feito na leitura: conversão do formato largo do DataBank para formato longo, descarte do rodapé, ausências gravadas como ".." e zeros espúrios nas séries de participação convertidos em ausência.

Modelagem:
    No CRISP-DM esta fase costuma incluir modelos estatísticos. Neste projeto ela não é um modelo preditivo, porque o charter exclui previsão da desindustrialização. Aplica-se como cálculo de indicadores: participação setorial no PIB, comparação entre subsetores industriais e comparação do Brasil com outros países no indicador de indústria de transformação. Scripts e resultados ficam em Code/modeling/ e Data/modeled/.

Avaliação:
    Verifica se as metas foram atendidas. Neste projeto, avaliar significa checar cobertura da série, origem de cada valor, coerência da soma agropecuária + indústria + serviços com o valor adicionado a preços básicos (não com 100% do PIB a preços de mercado), compatibilidade entre IBGE, Ipeadata e a literatura, identificação de mudanças metodológicas e uso da divulgação oficial mais recente.

Implantação:
    Coloca a solução à disposição do usuário. Neste projeto, a aplicação é o dashboard Streamlit em Scripts/app.py, com notas de implantação em Code/deployment/. O painel deve exibir a série setorial e a procedência dos dados, sem valores inseridos manualmente nas séries oficiais.

- TDSP: O ciclo de vida do TDSP tem um eixo horizontal (as fases) e um eixo vertical (os papéis). As fases horizontais são Business Understanding, Data Acquisition and Understanding, Modeling, Deployment e Customer Acceptance. Elas se aplicam a este projeto assim.

Business Understanding:
    O líder do projeto define problema, escopo, objetivos, critérios de sucesso e interessados. Neste projeto, o artefato é Docs/Project_Charter.md, com a identificação do problema na seção 1. É o equivalente ao entendimento do negócio do CRISP-DM e o ponto de partida do ciclo.

Data Acquisition and Understanding:
    O Data Scientist e o Data Engineer obtêm os dados e verificam se fazem sentido. Neste projeto, a aquisição tem três formas: extração via API no dashboard (SIDRA e Ipeadata, em Scripts/dados.py), scraping em script à parte (Code/data_acquisition/scrape_ods9.py) e arquivo exportado do DataBank para Data/raw/ (World Bank), que o usuário envia na página Comparação internacional. O entendimento é o mapeamento das fontes em Docs/Data_Summary_Report.md e as análises exploratórias em Code/data_exploration/. Esta fase alimenta a modelagem e pode voltar a ela se a qualidade dos dados não for suficiente (completude, origem, coerência entre fontes).

Modeling:
    O Data Scientist constrói a solução analítica. Neste projeto, modelar é produzir os indicadores de participação no PIB e as comparações setorial e internacional. Não há treinamento de modelo preditivo. O TDSP trata esta fase em ciclo com a aquisição: se a série for incompleta ou incompatível entre fontes, volta-se aos dados.

Deployment:
    O Solution Architect leva o produto ao ambiente de uso. Neste projeto, a implantação é o dashboard Streamlit (Scripts/app.py) e a documentação em Code/deployment/, incluindo ambiente Python (requirements.txt) e a organização das pastas. É o equivalente à implantação do CRISP-DM.

Customer Acceptance:
    O líder do projeto e o cliente confirmam se a entrega atende ao combinado. Neste projeto, o aceite confronta o painel com as metas da seção 1 e com o público descrito no charter (gestores de política industrial, federações, pesquisadores, áreas de ESG e demais interessados). No contexto acadêmico, o avaliador exerce esse papel de aceite.

Papéis no eixo vertical:
    Líder do projeto: escopo, charter e critérios de sucesso.
    Data Scientist e Data Engineer: fontes, extração, qualidade dos dados e indicadores. Solution Architect: estrutura TDSP do repositório, ambiente de execução e arquitetura do Streamlit.

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

A árvore abaixo segue as fases do TDSP. Cada pasta de código e de dados possui um README próprio, que descreve o conteúdo nela armazenado.

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
