# Modeling (TDSP)

Este README foi redigido com apoio de IA (Claude Opus 5.5 e Claude Haiku 5.5) e revisado pelo autor.

Indicadores derivados (participação setorial, comparação internacional).
Não há modelo preditivo (fora do escopo do charter).

Modelo de linguagem local (TP4), para resumos de texto:
- `baixar_modelo.py`: baixa `Qwen/Qwen3-0.6B` uma vez, com internet.
- `resumidor.py`: carrega o modelo do disco e gera resumos. Usado pela API (`Code/api/routers/texto.py`).
- `medir_modelo.py`: mede tempo, memória e fidelidade numérica no banco de textos. Resultado em `Data/modeled/resumos_qwen3_0_6b.csv`.
- Decisão e medições: `Docs/Escolha_do_modelo.md`.

## Como rodar (modelo de linguagem, TP4)

Modelo padrão: `Qwen/Qwen3-0.6B`. A variável de ambiente `MODELO_RESUMO` troca o
modelo nos três scripts e na API (ex.: `MODELO_RESUMO=Qwen/Qwen2.5-0.5B-Instruct`).

```
python Code/modeling/baixar_modelo.py          # uma vez, com internet
python Code/modeling/medir_modelo.py           # mede tempo, memória e fidelidade no banco de textos
```

`medir_modelo.py` grava um CSV por modelo em `Data/modeled/` (ver o README dessa pasta).
O banco de textos é montado na hora: justificativas das metas do ODS 9 com pelo menos
150 caracteres, os resumos de `Data/raw/referencias_resumos.csv`, e a introdução do
Oreiro e Feijó, lida ao vivo da página do SciELO.
