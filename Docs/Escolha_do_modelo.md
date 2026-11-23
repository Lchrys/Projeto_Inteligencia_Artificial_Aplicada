# Escolha do modelo de linguagem (TP4)

**Status:** modelo escolhido: **Qwen/Qwen3-0.6B**, com as falhas e os limites registrados na seção 3. O primeiro candidato foi descartado (seção 1).

## Requisitos

- Gerar resumos de textos em português sobre desindustrialização e o ODS 9.
- Rodar localmente, na CPU, sem nuvem.
- Ser baixável sem conta nem token (sem gated) e ter licença que permita o uso.
- Caber na memória da máquina de desenvolvimento, com folga para o sistema.

## Máquina de referência

- Processador: Intel Core i5-1035G1, 4 núcleos e 8 threads, sem GPU dedicada.
- Memória: 8 GB de RAM instalada, 7,74 GB utilizáveis.
- Sistema: Windows 11, 64 bits.

## 1. Tentativa com Qwen2.5-1.5B-Instruct (descartada)

**Modelo:** `Qwen/Qwen2.5-1.5B-Instruct`, carregado em float32 na CPU.

**O que foi feito**
1. Download dos pesos pelo Hugging Face, em 121 segundos, cerca de 3 GB em disco.
2. Carregamento do modelo, em 23 segundos.
3. Teste de geração de um texto, com limite de 60 tokens.

**O que aconteceu**
- Logo após o carregamento, o processo reportou cerca de 0,1 GB de memória. Isso indica que os pesos eram lidos do disco sob demanda, e não mantidos inteiros na RAM.
- A geração do primeiro texto não terminou em mais de 10 minutos. O processo foi interrompido manualmente, depois de consumir praticamente toda a memória e a CPU da máquina.

**Por que não funciona nesta máquina**
- Um modelo de 1,54 bilhão de parâmetros em float32 ocupa cerca de 6,2 GB só nos pesos (1,54 bi × 4 bytes).
- Com 7,74 GB utilizáveis, sobram cerca de 1,5 GB para o Windows, o Python, o cache de ativações e a própria execução. A folga não é suficiente.
- Quando a memória esgota, o sistema passa a paginar pesos pelo disco. Cada token passa a levar muito mais tempo, e a CPU fica ocupada com a troca de páginas, e não com a geração.

**Conclusão:** o problema é de limite de hardware, e não de código. Nesta máquina o modelo só caberia com precisão menor (bfloat16 ou int8) ou com mais memória; o projeto seguiu a outra saída, a de escolher um modelo menor (Qwen3-0.6B).

**Limites deste registro:** a causa é inferida a partir dos sintomas (memória esgotada, carregamento lento e consumo total da CPU). Não houve medição do uso de memória durante a geração nem do tempo por token.

## 2. Candidatos considerados

Tabela dos candidatos que entraram na análise, com o status e o motivo de cada
decisão. "Medido" significa rodado nesta máquina. "Ficha" significa descartado
antes do download, pela página do modelo no Hugging Face. Os tamanhos em float32
são estimativas: número de parâmetros × 4 bytes.

| Candidato | Tipo | Tamanho em float32 (estimado) | Status | Motivo |
|---|---|---|---|---|
| `Qwen/Qwen3-0.6B` | geração (instrucional) | cerca de 2,4 GB | **escolhido**; medido no banco de 10 textos | Cabe na máquina de 8 GB; tempo aceitável; licença Apache 2.0; sem gated; resumos em português com erros registrados |
| `Qwen/Qwen2.5-1.5B-Instruct` | geração (instrucional) | cerca de 6,2 GB | **descartado por hardware**; medido até o travamento | Os pesos sozinhos ocupam quase toda a RAM utilizável; o primeiro texto não terminou em mais de 10 min |
| `Qwen/Qwen2.5-0.5B-Instruct` | geração (instrucional) | cerca de 2 GB | **medido; descartado** | Mesmo procedimento no banco de 10 textos (ver seção "Comparação com o Qwen2.5-0.5B"). Inverteu o sentido de um resumo (Morceiro), misturou a tese dos ortodoxos na conclusão de outro (Oreiro e Feijó) e produziu uma palavra sem sentido (Rodrik). Dois alertas de cópia, contra um do Qwen3-0.6B |
| `Qwen/Qwen3-1.7B` | geração (instrucional) | cerca de 7 GB | **descartado por hardware** (ficha conferida em 16/11/2026) | Licença Apache 2.0, sem gated. 1,7 bilhão de parâmetros, cerca de 7 GB em float32: acima da memória utilizável com folga. A versão em bfloat16 não foi medida |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | geração (instrucional) | cerca de 7 GB | **descartado por idioma e hardware** (ficha conferida em 16/11/2026) | A ficha declara que o modelo entende e gera principalmente inglês, sem português declarado. Licença Apache 2.0, sem gated. Cerca de 1,7 bilhão de parâmetros, mesma faixa de memória do 1,5B, que já travou |
| `microsoft/Phi-3.5-mini-instruct` | geração (instrucional) | cerca de 15 GB | **descartado por hardware** (ficha conferida em 16/11/2026) | Licença MIT, sem gated, e suporta português. Cerca de 3,8 bilhões de parâmetros, cerca de 15 GB em float32: muito maior que a RAM disponível |
| `google/gemma-3-1b-it` | geração (instrucional) | cerca de 4 GB | **descartado por acesso** (ficha conferida em 16/11/2026) | Gated: exige aceitar as condições de uso no Hub antes de baixar. Licença própria (gemma). 1 bilhão de parâmetros. Quebra o requisito de baixar sem conta |
| `meta-llama/Llama-3.2-1B-Instruct` | geração (instrucional) | cerca de 4 GB | **descartado por acesso** (ficha conferida em 16/11/2026) | Gated: exige compartilhar informações de contato no Hub. Licença llama3.2. Suporta português, mas só o acesso já quebra o requisito de baixar sem conta. 1 bilhão de parâmetros |
| `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | classificação por NLI (zero-shot) | cerca de 1 GB | **descartado por tarefa** (ficha conferida em 16/11/2026) | Licença MIT, sem gated, 0,3 bilhão de parâmetros. Classifica pares de texto e não gera resumo |
| `neuralmind/bert-base-portuguese-cased` (BERTimbau) | modelo de máscara (fill-mask) | cerca de 0,4 GB | **descartado por tarefa** (ficha conferida em 16/11/2026) | Licença MIT, sem gated, 110 milhões de parâmetros, feito para português. Preenche lacunas e não gera texto nem segue instruções |

**Nota sobre as fichas:** as fichas dos modelos descartados sem medição foram conferidas em 16/11/2026, nas páginas do Hugging Face, sem download. Acesso (gated), licença, parâmetros, tarefa e idiomas declarados vêm dessas páginas. Os tamanhos em float32 são estimativas: número de parâmetros × 4 bytes. Os valores de Phi-3.5 e Llama-3.2 vieram de um resumo da página, e não da leitura integral, e devem ser reconferidos se a entrega exigir precisão. Nenhum dos descartados foi baixado.

### Comparação com o Qwen2.5-0.5B

Mesmo banco de 10 textos e mesmo procedimento. Resultados lado a lado:

| Medida | Qwen3-0.6B (escolhido) | Qwen2.5-0.5B |
|---|---|---|
| Tempo, mediana | 26,0 s | 21,3 s |
| Tempo, pior caso | 38,1 s | 67,9 s |
| Memória de pico | 2,41 GB | 1,93 GB |
| Alertas de cópia ou resumo curto | 1 | 2 |
| Erro de sentido (trechos verificados) | Oreiro e Feijó: "transformação" no lugar de "desindustrialização". Rodrik: trechos confusos | Morceiro: inverteu o sentido (participação "aumentada" após corrigir o dummy, quando o texto diz que ela estava superestimada). Oreiro e Feijó: apresentou a tese dos ortodoxos como conclusão do texto. Rodrik: palavra sem sentido ("Indígenas asiáticas") e frases incompletas |

O Qwen2.5-0.5B é um pouco mais rápido na mediana e usa menos memória, mas errou
mais nos três resumos de referência, que são os textos mais próximos do tema do
monitor. Por isso ele foi descartado, e o Qwen3-0.6B continua como escolhido.
Um dos erros do Qwen3-0.6B (Oreiro e Feijó) também é grave, e está registrado na
seção 3.

### Teste de um texto com o Qwen3-0.6B

- **Configuração:** float32, CPU, modo de raciocínio desligado (`enable_thinking=False`), limite de 80 tokens novos, entrada de 300 tokens.
- **Carregamento:** 6,6 s.
- **Memória:** cerca de 3,2 GB logo após o carregamento e 2,5 GB de pico durante a geração. Cabe nos 7,7 GB utilizáveis, com folga.
- **Velocidade:** 80 tokens em 21,9 s, cerca de 3,7 tokens por segundo.
- **Qualidade:** o resumo saiu em português e acompanha o texto, mas copiou a classificação JEL do metadado do artigo para dentro do resumo. Essa falha precisa ser medida no banco inteiro.

O teste completo no banco de provas do projeto está na seção "Medição no banco de 10 textos" abaixo. A comparação com o Qwen2.5-0.5B está na seção "Comparação com o Qwen2.5-0.5B".

### Primeira medição no banco de 10 textos (Qwen3-0.6B, antes das correções)

Estes números são da primeira rodada. Os números finais, depois das correções, estão na rodada seguinte.

Banco: 7 justificativas de metas do ODS 9 (com pelo menos 150 caracteres) e 3 resumos das referências. A meta 9.a foi excluída por ter justificativa curta demais (34 caracteres).

- **Tempo por resumo:** mediana de 19,8 s e pior caso de 33 s. O total ficou em cerca de 3,5 minutos.
- **Memória de pico:** 2,45 GB.
- **Fidelidade numérica:** só 3 dos 10 resumos têm números, e nos 3 todos os números aparecem no texto de origem. A conclusão vale só para esses 3 textos.
- **Qualidade:** os resumos são em português e, na leitura, acompanham o conteúdo de cada texto. A checagem de um dado específico (Pintec e ENCTI, meta 9.5) confirmou que estava na origem.

Falhas encontradas:
1. **Metadado copiado:** o resumo do Morceiro (2021) reproduziu a classificação JEL (E23; L16; O14), que não é conteúdo do texto.
2. **Rótulo copiado:** dois resumos começam com "Resumo:", repetindo o rótulo do prompt. Isso se corrige com pós-processamento simples.

Limite: o banco tem 10 textos e os números são de uma única máquina. Antes de decidir, falta a leitura humana de uma amostra e a checagem do que o modelo escreve além do que está no texto.

### Rodada final com as correções (Qwen3-0.6B)

Correções aplicadas: instrução no prompt para ignorar códigos de classificação e metadados, remoção do rótulo "Resumo:" na saída, e alertas automáticos (`curto` para resumo com menos de 80 caracteres e `copia_do_texto` para resumo com mais de 80% do texto de origem). O limite de 80 caracteres é provisório: foi definido a partir de 10 textos e de um único caso de título repetido, e não é um critério validado. Um limite relativo ao tamanho do texto de origem seria mais justo, mas os dados disponíveis não bastam para calibrá-lo.

- **Tempo:** mediana de 22,6 s por resumo e pior caso de 34,4 s.
- **Memória:** pico de 2,45 GB.
- **Metadado copiado (JEL):** eliminado nesta rodada.
- **Rótulo "Resumo:":** eliminado nesta rodada.
- **Alertas:** 2 em 10 resumos.
  - *meta-9.4, `copia_do_texto`:* o resumo tem 81% do tamanho do texto de origem, que é curto (203 caracteres). Precisa de leitura humana para decidir se é cópia de fato.
  - *Oreiro e Feijó (2010), `curto`:* o modelo repetiu o título em inglês ("De-industrialization: concept, causes, effects and the Brazilian case."). É falha do modelo com textos em inglês, e persistiu mesmo com a instrução corrigida.

**Limite do alerta:** a checagem mede tamanho e cópia, mas não avalia o sentido. Um resumo pode passar sem alerta e ainda estar errado ou mal escrito. O resumo do Rodrik (2016), que na rodada anterior tinha erros de português, não foi relido nesta rodada.

### Rodada com a introdução do Oreiro e Feijó (2010)

O abstract em inglês do Oreiro e Feijó foi substituído pela introdução em português, extraída da página do SciELO, salva em `Data/raw/oreiro_feijo_2010_introducao.txt` e lida desse arquivo a cada execução. O CSV de medição guarda só o resumo gerado.

- **Tempo:** mediana de 26,0 s por resumo e pior caso de 38,1 s.
- **Memória:** pico de 2,41 GB.
- **Alertas:** 1 em 10 (meta-9.4, `copia_do_texto`). O resumo do Oreiro e Feijó não gerou alerta, porque deixou de repetir o título.
- **Conteúdo do resumo do Oreiro e Feijó:** em português e próximo do texto, mas com um erro relevante. Ele diz que a economia "passou por uma transformação" causada pela abertura financeira e pela apreciação cambial, quando o texto fala de **desindustrialização**. Também omite o rótulo "novo-desenvolvimentista". A segunda metade (a posição dos ortodoxos, que atribuem à apreciação cambial um efeito favorável à indústria) está correta.

O erro é do tipo que o monitor não pode aceitar: a palavra "transformação" é o nome do setor medido pelo projeto. Por isso o resumo do Oreiro e Feijó só pode ser usado com revisão humana, e a checagem automática não o pegaria.

**Leitura humana dos resumos sinalizados:**
- **Oreiro e Feijó (2010): reprovado.** Erro de termo descrito acima.
- **Rodrik (2016): reprovado.** O resumo inverte um fato: diz que os países asiáticos e os exportadores de manufaturados foram afetados pela desindustrialização, quando o texto diz que foram protegidos. Também tem erros de português. Não pode ser usado sem reescrita.
- **meta-9.4: aceito com ressalva.** O resumo é fiel ao texto, mas quase repete a frase original. O alerta de cópia é correto, e aqui não indica erro, porque o texto de origem é curto.

**Decisão:** o Qwen3-0.6B foi aceito como modelo do projeto, com estes limites:
1. Textos em inglês podem gerar resumos que repetem o título, como no caso do Oreiro e Feijó. Quando o alerta `curto` aparece, o resumo deve ser lido com desconfiança antes de qualquer uso.
2. A checagem numérica depende de textos com números. Só 3 dos 10 textos têm números, então a fidelidade numérica medida vale para esses 3.
3. O banco tem 10 textos, medidos numa única máquina.

## 3. Justificativas da decisão

**Por que o Qwen3-0.6B.**
- **Cabe na máquina de referência:** pico de 2,41 GB de memória, contra 7,7 GB utilizáveis. Rodou sem travar a máquina, como o Qwen2.5-0.5B, mas errou menos nos textos do tema (seção 2).
- **Tempo aceitável:** mediana de 26 s por resumo e pior caso de 38 s, em 10 textos.
- **Baixa sem conta:** o download funcionou sem token, o que atende ao requisito de acessibilidade do projeto.
- **Português:** os resumos saem em português, e a maioria acompanha o texto de origem.

**Por que não o Qwen2.5-0.5B-Instruct.** Foi medido no mesmo banco e errou mais nos resumos de referência: inverteu o sentido de um resumo e misturou posições em outro (seção 2). Era o candidato mais leve, e a diferença de memória não compensou.

**Por que não o Qwen2.5-1.5B-Instruct.** Em float32, ocupa cerca de 6,2 GB só nos pesos. Na máquina de referência, a memória esgotou e o processo foi interrompido sem terminar o primeiro texto (seção 1).

**Por que não modelos maiores.** Modelos com cerca de 1,7 bilhão de parâmetros ou mais (7 GB ou mais em float32) não cabem com folga nesta máquina. Modelos gated, que exigem aceitar as condições de uso ou compartilhar informações no Hub (como Gemma e Llama), estão fora do requisito de acesso sem conta.

**Limite conhecido, aceito conscientemente.** A medição mostrou erros de sentido em resumos: um inverte um fato (Rodrik, 2016), outro troca um termo (Oreiro e Feijó, 2010). Esses erros não aparecem em tempo nem em memória, e a checagem automática não os detecta. O modelo foi mantido porque é o único que cabe nas restrições medidas, com as condições abaixo.

**Condições para uso do modelo no projeto, e o que já está implementado:**
1. Nenhum resumo gerado é exibido como fato sem revisão humana prévia. **Parcial:** a API e a aba Resumo mostram o aviso de revisão, mas a revisão em si é uma decisão de uso, não uma verificação do código.
2. Resumos muito curtos (alerta `curto`) não devem ser usados sem leitura. **Não implementado na API:** a rota devolve o resumo mesmo quando ele é curto. A checagem de tamanho existe só no script de medição, com um limite provisório de 80 caracteres.
3. Textos em inglês são evitados como entrada sempre que houver versão em português. **Recomendação de uso:** a API aceita qualquer texto, e a escolha da entrada é de quem usa.
4. Resumos de textos com números passam pela checagem de fidelidade numérica. **Não implementado na API:** a checagem existe no script de medição e no teste com o modelo real.
5. A API indica, em cada resposta, o motor usado e que o resumo é gerado por modelo e sujeito a revisão. **Implementado:** campos `motor` e `aviso`.

**Licença verificada.** O cartão do modelo no Hugging Face (`Qwen/Qwen3-0.6B`) declara licença **Apache 2.0** e não é gated, ou seja, não exige pedido de acesso. A verificação foi feita em leitura direta da página.

## 4. Integração local (critério 2 da rubrica)

A descrição completa está em `Code/api/README.md`. Resumo dos passos:

1. **Ambiente:** `pip install -r requirements.txt`. Bibliotecas: `transformers` (carregar e gerar), `torch` (execução, versão de CPU), `huggingface_hub` (download), `psutil` (medição de memória, só na medição) e `httpx` (testes). A lista completa está em `Code/api/README.md`. O `torch` é a versão só de CPU, apontada por `--extra-index-url` no próprio arquivo, para a instalação não baixar CUDA.
2. **Download:** `.venv\Scripts\python.exe Code/modeling/baixar_modelo.py` baixa `Qwen/Qwen3-0.6B` (cerca de 1,5 GB) para o cache do Hugging Face, fora do Git.
3. **Carga na subida:** `Code/api/main.py` tem um `lifespan` que chama `carregar_na_subida()`. O modelo é lido do disco com `local_files_only=True`, em float32 na CPU. Se a carga falhar, a API sobe mesmo assim e só `POST /processar_texto` responde 503.
4. **Rota:** `Code/api/routers/texto.py` declara a rota com `def`, porque a geração calcula na CPU e bloquearia o laço assíncrono. A geração roda numa thread separada, com tempo limite de 120 s (504).
5. **Sem internet:** com `HF_HUB_OFFLINE=1`, a API sobe e responde normalmente, o que prova que a integração é local.

**Ajustes para o hardware:** float32 (cerca de 2,4 GB de RAM, contra 7,7 GB utilizáveis); modo de raciocínio do Qwen3 desligado (`enable_thinking=False`); uma geração por vez, para não disputar a memória de 8 GB.

**Testes:** `.venv\Scripts\python.exe -m unittest discover -s Code/api/tests -t .` cobre 422, 502, 503, 504, 500 e o formato da resposta 200, com modelo falso. O teste com o modelo real (`RODAR_MODELO_REAL=1`) confere a integração de fato: carga na subida, formato da resposta, resumo não vazio, tamanho, tempo e números.

## 5. Uso de IA

Este projeto usou ferramentas de IA, conforme o enunciado exige citar:

- **Ferramenta:** Claude (Anthropic), modelos Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5, usados no Claude Code, em conversa com o autor.
- **Para quê:** planejamento das etapas, escrita de código (scrapers, módulos de modelo, rotas, testes), redação da documentação e revisão de textos.
- **Verificação:** o autor conferiu os resultados. O código foi executado e os testes foram rodados; os resumos do modelo foram lidos e comparados com os textos de origem, e os erros encontrados estão registrados na seção 3.
- **Responsabilidade:** as decisões de escopo, de fonte e de modelo são do autor, e o modelo gerou apenas os resumos avaliados aqui.
