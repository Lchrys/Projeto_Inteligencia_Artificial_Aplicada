# Routers da API

Objetivo: separar as rotas por assunto, para cada arquivo cuidar de um conjunto de endpoints.

- `series.py`: séries oficiais (Ipeadata) e envio do CSV do DataBank (`/serie/transformacao`, `/world-bank`).
- `ods9.py`: metas do ODS 9 extraídas do Ipea (`/ods9/metas`, `/ods9/metas/{codigo}`).
- `texto.py`: análise de texto com o modelo de linguagem local (`/processar_texto`). Carrega o modelo na subida e responde 503, 502 e 504 conforme o caso.

Os modelos de entrada e saída de cada rota ficam em `Code/api/models.py`. Os erros
comuns ficam em `Code/api/erros.py`. A montagem dos routers acontece em `Code/api/main.py`.
