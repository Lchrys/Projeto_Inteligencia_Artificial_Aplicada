# Teste do chat com exemplos reais (TP5)

**Status:** 24 casos rodados contra a OpenAI com `gpt-4.1-mini`, sem erro; resumo no README da raiz (seção 4.4).

## Como o teste roda

`Code/modeling/testar_assistente.py` roda **24 casos** contra a OpenAI, com os dados reais e os filtros padrão de
cada página, e grava `Data/modeled/chat_openai_casos.csv` (pergunta, o que se esperava, resposta, tempo, números
fora das tabelas, contas conferidas e fonte exibida). Cada página é uma conversa com memória: as perguntas seguintes dependem das anteriores.

## Os 24 casos

| Página | Casos | O que testa |
|---|---|---|
| Série histórica | 9 | Perda desde 1995, maior valor, valor em 2010, "e em 2011?", "qual a diferença?" (conta conferida), ano fora do intervalo da tela (1980), previsão, pergunta fora do tema, tentativa de forçar um valor |
| Panorama setorial | 6 | Peso de serviços e indústria, transformação dentro da indústria, transformação × agropecuária, pergunta com premissa falsa, valor de um trimestre, dado inexistente (emprego) |
| Comparação internacional | 9 | Comparação com outros países, "e em 2024?", 2010, 1990, Brasil × Alemanha, indicador que não está selecionado, quem mais perdeu desde 1995 (contas), EUA sem dado em 2024, tentativa de forçar o ranking |

## Resultado da última rodada

Com o `gpt-4.1-mini`: 24 respostas sem erro, de 0,9 a 2,6 s cada. Todas foram conferidas
contra o "esperado" do teste e todas o cumpriram. Nenhum número ficou fora das tabelas sem explicação. Em 3 respostas o
modelo fez contas (por exemplo, "qual a diferença?" entre 14,97% e 13,86%: 1,11 p.p.), 5 contas ao todo, e o
código conferiu todas. A fonte das tabelas aparece sob as 24 respostas (coluna `fontes_exibidas` do CSV); em 17
delas o modelo também a cita no texto.

## O que o teste achou e foi corrigido

O CSV guarda só a última rodada.

- **Resumos escolhidos de antemão.** A primeira versão dava ao modelo fatos pré-calculados (último valor, máximo,
  ranking); "e em 2024?" falhava ("o painel não inclui 2024"), embora o dado estivesse na aplicação, e cada tipo de
  pergunta pedia uma regra nova. Hoje cada página entrega as próprias tabelas.
- **Checagem de números.** Três defeitos: "1995,16.81" (CSV separado por vírgula) era lido como um número só;
  formatos brasileiros ("3.277.790", "712.716,0") eram sinalizados à toa; e o Streamlit lia `$...$` como fórmula e
  engolia o texto entre dois "R$" (agora o cifrão é escapado na exibição).
- **Série inteira (79 linhas).** O `gpt-4o-mini` errou o maior valor desde 1995 e negou ter 1980, que estava na
  tabela. Passaram a valer: ano mais recente primeiro, resumo calculado pelo código (extremos) separado antes e
  depois de 1995, e contexto restrito ao que a tela mostra.
- **Contas.** A primeira regra do prompt proibia contas, e o assistente respondia "a página não traz o cálculo" a
  "qual a diferença?". Agora ele calcula diferença, soma e variação percentual mostrando os valores usados, e o
  código refaz a conta; sem os valores na resposta, ou com a conta errada, vira aviso.
- **"E em 1990?" na Comparação.** O `gpt-4o-mini` negou o dado do Brasil (22,83% no CSV) ou disse que a tabela
  começava em 1991: a tabela larga e esparsa o fazia contar vírgulas. Medidas: a célula sem valor passou a ser
  escrita "sem dado", e o modelo padrão passou para o `gpt-4.1-mini`. Em 5 repetições da conversa (comparação,
  "e em 2024?", "E em 1990?"), medindo se a resposta traz 22,83%: `gpt-4o-mini` com "sem dado", 3 de 5; `gpt-4o`,
  5 de 5; `gpt-4.1-mini`, 5 de 5, que ficou por ser menor e mais barato. Antes do "sem dado", em 3 repetições, o
  `gpt-4o-mini` acertou 1 e o `gpt-4o`, 2.
- **Fonte.** O modelo não a citava em nenhuma das 9 respostas da Comparação. Agora o código exibe a fonte das
  tabelas sob toda resposta (teste automático), e a citação no texto é só reforço.
- **Respostas vazias de conteúdo.** "Desculpe, mas não posso fazer isso" e um pedido de "o ano, o país ou o indicador
  específico" para uma pergunta sobre emprego vinham da regra 2 (que mandava dizer "o que falta" mesmo sem sentido)
  e da falta de uma regra para pedidos de ignorar as regras. O prompt passou a recusar em uma frase, dizendo o que
  as tabelas mostram (regra 11), e a pedir o que falta só quando faz sentido.

## O que o teste cobre

24 casos com o modelo padrão, mais as repetições citadas acima. A redação do modelo varia
a cada chamada; o que o código assegura em toda chamada é a conferência dos números e a exibição da fonte. A conta
conferida, exibida sob a resposta, mostra de onde cada número veio e prova a aritmética; qual comparação faz sentido
é leitura de quem usa o painel, e por isso a resposta avisa quando os períodos diferem (em "quem mais perdeu desde
1995?", a China começa em 2004 e os EUA em 1997).
