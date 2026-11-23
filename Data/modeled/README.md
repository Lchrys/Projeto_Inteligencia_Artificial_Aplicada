# Data / modeled

Este README foi redigido com apoio de IA (Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5) e revisado pelo autor.

Saídas de modelagem e indicadores calculados.

## Medições de modelos de linguagem (TP4)

- `resumos_qwen3_0_6b.csv`: medição do modelo escolhido (Qwen/Qwen3-0.6B) nos 10 textos do banco. Uma linha por resumo, com tempo, memória, fidelidade numérica, alerta e o resumo gerado.
- `resumos_qwen2_5_0_5b_instruct.csv`: a mesma medição com o Qwen2.5-0.5B, usada na comparação. Descartado, com o motivo em `Docs/Escolha_do_modelo.md`.

## Conversa de teste do assistente (TP5)

- `chat_openai_casos.csv`: 24 casos em 3 conversas, uma por página (série histórica, panorama setorial e comparação internacional), gerados por `Code/modeling/testar_assistente.py` com a OpenAI (`gpt-4.1-mini`) e os filtros padrão de cada tela. Colunas: pagina, pergunta, o que se esperava, resposta, motor, segundos, números fora do contexto, contas conferidas pelo código e fonte exibida sob a resposta. Inclui perguntas de memória ("e em 2024?"), de ano fora da seleção da tela, de dado inexistente, de premissa falsa e de tentativa de forçar um valor.

Nos arquivos do TP4, o nome do arquivo segue o modelo. Os resultados e a decisão estão em `Docs/Escolha_do_modelo.md`.
