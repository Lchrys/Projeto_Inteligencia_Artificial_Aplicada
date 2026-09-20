# Data Summary Report: monitor-desindustrializacao

# Hierarquia das fontes

As fontes não têm o mesmo peso no painel. A ordem abaixo evita ler como equivalentes séries que medem coisas diferentes.

- Fonte principal: Ipeadata (SCN10_VAITY10, via API) e World Bank (NV.IND.MANF.ZS, via arquivo do DataBank). São o indicador 9.2.1 da ONU (indústria de transformação em proporção do PIB) em série anual longa. O World Bank é o que sustenta a comparação internacional.
- Fonte de composição: IBGE/SIDRA, tabela 1846 (Fontes 1 e 2). Mostra a estrutura setorial e a abertura da indústria em subsetores, no trimestre mais recente. Serve para separar manufatura (90693) do agregado indústria (90691), não para demonstrar tendência.
- Fonte de contexto: página ODS 9 do Ipea (Fonte 5, scraping). Texto, não série.

# Ressalvas de método

Valem para todo o painel. Detalhe e bibliografia em [Referencias.md](Referencias.md).

1. Ipeadata e World Bank não são evidência independente do IBGE: ambos compilam contas nacionais. A diferença é frequência, classificação e defasagem.
2. No SIDRA, "indústria" (código 90691) é o agregado (extrativa, transformação, construção e utilities); transformação é o código 90693. O agregado pode se sustentar enquanto a manufatura recua.
3. As séries do SIDRA e do Ipeadata estão a preços correntes, então a participação setorial no PIB também se move por preço relativo, e não apenas por volume produzido (Oreiro e Feijó, 2010; Morceiro, 2021).
4. A redação da ONU para a meta 9.2 pede aumentar a participação da indústria no PIB e no emprego. A redação adaptada pelo Ipea deslocou o foco para produtividade e complexidade tecnológica. As séries medem o indicador da ONU; o texto do Ipea entra como ressalva oficial brasileira.
5. O painel cobre o componente "em proporção do PIB" do indicador 9.2.1; o componente per capita não entra nesta etapa.
6. Só de 1995 em diante os níveis das Contas Nacionais brasileiras são comparáveis. Há quebras em 1989–90 e 1994–95 por mudança de referência, não por desindustrialização (Morceiro, 2021).

Formas de extração: SIDRA (Fontes 1 e 2) e Ipeadata (Fonte 3) são consultados por API, ao vivo, com cache de uma hora no Streamlit. A página ODS 9 do Ipea (Fonte 5) é extraída por scraping em script separado. O World Bank (Fonte 4) entra por arquivo exportado do DataBank e guardado em `Data/raw/`. Em nenhum caso há valor digitado à mão: as tabelas baixadas do painel registram fonte, código da série e data de extração.

# Fonte 1: IBGE/SIDRA, Contas Nacionais Trimestrais

Fonte: IBGE, Sistema de Recuperação Automática (SIDRA), pesquisa "Contas Nacionais Trimestrais", tabela 1846 (valores a preços correntes). São utilizados o PIB a preços de mercado e o valor adicionado por agropecuária, indústria e serviços (códigos 90707, 90687, 90691 e 90696).

Tipo de dado: série temporal trimestral, estruturada e quantitativa. Pela ajuda da API Sidra (https://apisidra.ibge.gov.br/home/ajuda), o retorno é JSON ou XML, com nomes/códigos em texto e o campo "V" (número ou caractere especial). Unidade: milhões de reais. O descritor da tabela 1846 (https://sidra.ibge.gov.br/tabela/descricao/1846) lista setores e PIB a preços de mercado, alinhado a este recorte.

Objetivo de uso: mostrar a estrutura setorial no trimestre mais recente, para separar o agregado indústria da transformação. A participação de cada setor é o valor adicionado sobre o PIB a preços de mercado; agropecuária + indústria + serviços não somam 100% desse PIB, porque os impostos líquidos sobre produtos ficam de fora do VA setorial. A coerência da soma se verifica no valor adicionado a preços básicos.

O painel consulta o último trimestre disponível (`periodos/-1`) via API Agregados v3. É uma foto conjuntural: a trajetória de longo prazo, que é o objeto da desindustrialização, vem das Fontes 3 e 4. A série histórica trimestral fica para etapa posterior.

# Fonte 2: IBGE/SIDRA, subsetores industriais (tabela 1846)

Fonte: a mesma tabela 1846. Os subsetores industriais já estão nessa tabela (transformação 90693, extrativas 90692, construção 90694, eletricidade/gás/água 90695). Não há, no SIDRA, uma tabela anual do SCN com essa mesma desagregação exposta da mesma forma.

Tipo de dado: série temporal trimestral, estruturada e quantitativa. Contrato da API Sidra igual ao da Fonte 1.

Objetivo de uso: comparar a indústria de transformação com os demais subsetores industriais. O painel consulta o último trimestre disponível.

# Fonte 3: Ipeadata

Fonte: Ipeadata (Ipea), série SCN10_VAITY10 (PIB - indústria - transformação - preços correntes, % PIB), compilada a partir do IBGE/SCN Anual.

Tipo de dado: série temporal anual, estruturada e quantitativa. Pela documentação da API
(https://www.ipea.gov.br/portal/categorias/2-uncategorised/1825-api), série numérica tem "VALVALOR" float, "VALDATA" datetime e "SERCODIGO" varchar. A extração no painel usa ipeadatapy (OData4 ValoresSerie), na série completa disponível.

Objetivo de uso: é a série principal do painel para o indicador 9.2.1 da ONU (participação da indústria de transformação no PIB) no maior período disponível. Não é validação independente do IBGE: o Ipeadata compila o próprio SCN, em frequência anual. A checagem cruzada cabe ao World Bank (Fonte 4, outra classificação e outra defasagem) e à literatura (seção Fontes previstas).

O slider do painel abre em 1995, o primeiro ano em que os níveis das Contas Nacionais são comparáveis. A série completa permanece disponível; o aviso de quebra metodológica aparece quando o período atravessa 1995. A completude do recorte selecionado é exibida na página.

Validação cruzada: Morceiro (2021, p. 705–711) documenta a série oficial do SCN no mesmo conceito (indústria de transformação em % do PIB a preços correntes) e registra 16,8% em 1995 no SCN Referência 2010, o mesmo vintage que o Ipeadata compila a partir daí. A queda oficial de 26,8% (1994, SCN Ref. 1985) para 16,8% (1995, SCN Ref. 2010) é a quebra de referência, não desindustrialização; na série encadeada do autor, 1994 cairia para 18,8%, uma perda de 2 p.p. O critério de sucesso (completude acima de 90% dos anos com valor a partir de 1995) aplica-se a essa série no recorte comparável, e o painel mostra o percentual do intervalo escolhido.

# Fonte 4: World Bank, Indicadores de Desenvolvimento Mundial

Fonte: World Bank, World Development Indicators, exportado do DataBank (https://databank.worldbank.org/source/world-development-indicators). São utilizados indicadores de participação setorial no PIB (agropecuária NV.AGR.TOTL.ZS, indústria total NV.IND.TOTL.ZS, transformação NV.IND.MANF.ZS, serviços NV.SRV.TOTL.ZS), crescimento da transformação (NV.IND.MANF.KD.ZG) e exportações de alta tecnologia (TX.VAL.TECH.MF.ZS).

Forma de extração: arquivo exportado à parte, não consulta de API no painel. O arquivo é `Data/raw/world_bank_setorial.csv`, com 10 economias (Brasil, Estados Unidos, China, Rússia, Índia, Itália, França, Reino Unido, Alemanha e Japão) × 6 indicadores, de 1960 a 2025: 3.960 observações, das quais 2.249 têm valor (57%). Essa taxa descreve o arquivo inteiro, inclusive países e anos fora do recorte comparável (Brasil antes do fim dos anos 1970, em que o DataBank grava zero no lugar de ausência, e anos sem divulgação). O critério de 90% vale para a série do indicador 9.2.1 a partir de 1995, no recorte que o usuário filtra; o painel exibe a completude desse recorte, não a do arquivo bruto. O rodapé do próprio export registra a atualização da base pelo World Bank em 13/07/2026. O painel não lê esse arquivo sozinho: ele fica em `Data/raw/` como exemplo para download; filtros, gráficos e tabela só aparecem depois do upload na página Comparação internacional. A escolha pelo arquivo segue o mesmo padrão do scraping: extração fora do app, dado em `Data/raw/`. Por isso a comparação internacional não depende da disponibilidade das APIs do SIDRA e do Ipeadata.

Tipo de dado: série temporal anual, estruturada e quantitativa. O export do DataBank vem em formato largo (colunas `Country Name`, `Country Code`, `Series Name`, `Series Code` e uma coluna por ano no padrão `1960 [YR1960]`), com ausências gravadas como `..` e três linhas de rodapé no fim do arquivo. O painel converte para formato longo, descarta o rodapé e trata `..` como ausente. A ficha técnica de cada série está em `Data/raw/world_bank_setorial_metadata.csv`: unidade, periodicidade anual, método de agregação, limitações e licença CC BY 4.0.

Objetivo de uso: comparar a trajetória brasileira com a de outros países nos indicadores do recorte, com gráficos de evolução, comparação em um ano e composição setorial. Os filtros de país, indicador e período são derivados do próprio arquivo, e o usuário pode enviar outro export do DataBank pela interface. O download entrega o recorte já filtrado, com fonte, código da série e data de extração.

Qualidade dos dados, dois problemas identificados e tratados. Primeiro: o DataBank grava `0` onde o dado não existe em séries de participação, e o Brasil aparece com 0% de 1960 até o fim dos anos 1970; o painel converte esses zeros em ausência nos indicadores `.ZS`, para não desenhar uma queda que não existe. Segundo: a transformação brasileira cai de 23,7% para 14,5% do PIB entre 1994 e 1995 no World Bank, e há outro salto entre 1989 e 1990: são mudanças de referência das Contas Nacionais, não desindustrialização. Só de 1995 em diante os níveis são comparáveis, e o painel avisa quando o período selecionado atravessa esse ano. Esse é o risco de revisão metodológica previsto no Project Charter, agora materializado no dado.

Divergência entre fontes do mesmo conceito: para 1981 o World Bank reporta 34,4% de transformação no PIB brasileiro, enquanto o Ipeadata (Fonte 3) trabalha em outro nível na mesma época: a série anual do SCN parte de 19,9% em 1947 e chega a 11,8% em 2025. As duas medem o indicador 9.2.1, mas com classificação e vintage diferentes. A comparação entre elas é de tendência, não de nível.

# Fonte 5: Ipea, página ODS 9 (web scraping)

Fonte: Ipea, página "ODS 9 - Indústria, Inovação e Infraestrutura" (https://www.ipea.gov.br/ods/ods9.html). Extração com Beautiful Soup, em script separado (`Code/data_acquisition/scrape_ods9.py`), sem API.

Tipo de dado: texto estruturado em HTML. Cada meta vira uma linha com código, redação da ONU, redação adaptada ao Brasil, justificativa, conceitos e indicadores. O corpus concatenado fica em TXT. Arquivos: `Data/raw/ods9_metas.csv` e `Data/raw/ods9_corpus.txt`.

Volume extraído: 8 metas (9.1 a 9.c), com data de extração registrada em cada linha do CSV, em UTF-8. O script roda à parte; a aplicação apenas lê os arquivos já gravados em `Data/raw/`.

Objetivo de uso: contextualizar o recorte do painel. O indicador 9.2.1 extraído do texto ("valor adicionado da indústria em proporção do PIB") é o mesmo conceito das séries oficiais (IBGE/SIDRA, Ipeadata, World Bank NV.IND.MANF.ZS); o painel cobre só o componente em proporção do PIB, não o per capita. A interface exibe o texto da meta escolhida, a nuvem de palavras e a frequência das palavras. Por padrão, nuvem e frequência usam a meta selecionada (redação da ONU, redação brasileira, justificativa e conceitos); o corpus das oito metas permanece como opção.

# Fontes previstas

Não entram na extração desta etapa. Permanecem mapeadas para trabalho posterior.

## Banco Central do Brasil, SGS

Fonte: Banco Central do Brasil, Sistema Gerenciador de Séries Temporais (SGS), endpoint api.bcb.gov.br/dados/serie. Serão utilizados indicadores de produção industrial e de atividade econômica setorial.

Tipo de dado: série temporal mensal, estruturada e quantitativa. No portal de Dados Abertos do BCB (https://dadosabertos.bcb.gov.br/), o JSON do SGS traz os campos "data" e "valor" como texto.

Objetivo de uso: acrescentar ao dashboard uma leitura de curto prazo da indústria, junto à série de contas nacionais. A produção industrial mede ciclo, não estrutura: pode crescer enquanto a participação da transformação no PIB cai.

## Estudos publicados

Fonte: artigos já publicados sobre desindustrialização brasileira. Não é extração por API. A validação cruzada desta etapa usa Morceiro (2021), confrontado com a série do Ipeadata na Fonte 3. Demais referências (Tregenna, Oreiro e Feijó, Palma, Rodrik, Rowthorn e Ramaswamy) estão em [Referencias.md](Referencias.md).
