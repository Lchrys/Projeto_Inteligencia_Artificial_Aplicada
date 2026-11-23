# Testes da API

Este README foi redigido com apoio de IA (Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5) e revisado pelo autor.

Objetivo: verificar as regras da API sem depender de rede nem de um modelo pesado,
e, quando pedido, confirmar a integração com o modelo real.

- `test_texto.py`: testes rápidos da rota `POST /processar_texto`, com modelo falso.
  Cobrem 422, 503, 502, 504, 500 e o formato da resposta 200. Rodam sempre.
- `test_assistente.py` (TP5): o assistente de chat (`Code/modeling/assistente.py`) e o contexto de cada página (`Scripts/contextos.py`), com a OpenAI simulada. Cobrem a montagem do contexto (tabelas, resumo calculado, ordem dos anos, divisão em 1995, filtros, célula "sem dado"), a memória (limite de trocas), a checagem de números (vírgula do CSV, formato brasileiro, números inventados) e de contas (diferença, soma, variação percentual e razão, aceitas só com os valores na resposta), a fonte das tabelas devolvida com cada resposta e o mapeamento dos erros da OpenAI (401, 429, 5xx, tempo esgotado, sem internet). Rodam sempre, sem rede e sem chave.
- `test_chat.py` (TP5): a rota `POST /chat` (200, 422, 429, 502, 503, 504 e 500), o cliente `conversar` do painel, a mensagem que o chat mostra quando a API está fora do ar ou devolve erro (`Scripts/chat_pagina.py`) e a subida automática da API junto com o painel (`subir_api_se_preciso`), com a OpenAI simulada. Rodam sempre, sem rede e sem chave.
- `test_modelo_real.py`: integração com o Qwen3-0.6B de verdade. Demora cerca de um
  minuto e só roda com `RODAR_MODELO_REAL=1`.

Comandos, da raiz do projeto:

```
.venv\Scripts\python.exe -m unittest discover -s Code/api/tests -t .
set RODAR_MODELO_REAL=1
.venv\Scripts\python.exe -m unittest Code.api.tests.test_modelo_real -v
```

Detalhes e a justificativa do teste com modelo real estão em `Code/api/README.md`.
