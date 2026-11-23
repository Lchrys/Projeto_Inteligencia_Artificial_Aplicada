# Modeling (TDSP)

Este README foi redigido com apoio de IA (Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5) e revisado pelo autor.

Indicadores derivados (participação setorial, comparação internacional).
Não há modelo preditivo (fora do escopo do charter).

Assistente de chat (TP5):
- `testar_assistente.py`: roda 24 casos reais contra a OpenAI, três conversas (uma por página), e grava `Data/modeled/chat_openai_casos.csv`. Comando: `.venv\Scripts\python.exe Code\modeling\testar_assistente.py`.
- `assistente.py`: o assistente de chat, genérico: prompt de sistema, montagem do contexto (`tabela_para_contexto`, `resumo_temporal`), memória limitada, chamada à OpenAI e checagem dos números da resposta (`conferir_numeros`: números fora do contexto e contas conferidas). Cada página entrega o contexto (`Scripts/contextos.py`). A chave vem de `OPENAI_API_KEY` (ambiente ou `.env`).

Modelo de linguagem local (TP4), para resumos de texto:
- `baixar_modelo.py`: baixa [`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B) uma vez, com internet.
- `resumidor.py`: carrega o modelo do disco e gera resumos. Usado pela API (`Code/api/routers/texto.py`).
- `medir_modelo.py`: mede tempo, memória e fidelidade numérica no banco de textos. Resultado em `Data/modeled/resumos_qwen3_0_6b.csv`.
- Decisão e medições: `Docs/Escolha_do_modelo.md`.

## Como rodar (modelo de linguagem, TP4)

Modelo padrão: `Qwen/Qwen3-0.6B`. A variável de ambiente `MODELO_RESUMO` troca o
modelo nos três scripts e na API (ex.: `MODELO_RESUMO=Qwen/Qwen2.5-0.5B-Instruct`).

```
.venv\Scripts\python.exe Code/modeling/baixar_modelo.py          # uma vez, com internet
.venv\Scripts\python.exe Code/modeling/medir_modelo.py           # mede tempo, memória e fidelidade no banco de textos
```

`medir_modelo.py` grava um CSV por modelo em `Data/modeled/` (ver o README dessa pasta).
O banco de textos é montado na hora: justificativas das metas do ODS 9 com pelo menos
150 caracteres, os resumos de `Data/raw/referencias_resumos.csv`, e a introdução do
Oreiro e Feijó, salva em `Data/raw/oreiro_feijo_2010_introducao.txt`.
