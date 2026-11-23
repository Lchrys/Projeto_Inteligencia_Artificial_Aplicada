# Scripts (painel Streamlit)

Este README foi redigido com apoio de IA (Claude Opus 5.5, Claude Haiku 5.5 e Claude Sonnet 5.5) e revisado pelo autor.

Objetivo: o painel que o usuário vê. Cada arquivo tem um papel:

- `app.py`: ponto de entrada do painel e página Início.
- `nucleo.py`: carga e cálculo das séries, sem Streamlit. Usado pelo painel e pela API.
- `dados.py`: funções de carga com cache do Streamlit, em volta de `nucleo.py`.
- `cliente_api.py`: chama a API local; se ela não responder, o painel lê direto de `nucleo.py`. No TP5, `conversar` envia o chat a `POST /chat`, e `garantir_api` sobe a API junto com o painel (uma vez por servidor), se ela for local e ainda não estiver no ar.
- `interface.py`: avisos, métricas, gráficos e botões de download comuns às páginas. No TP5, `faixa_ciclo` (etapas do ciclo de dados, no Início).
- `contextos.py` (TP5): monta, a partir das tabelas de cada página, o texto que vai ao assistente (`contexto_serie`, `contexto_panorama`, `contexto_comparacao`). Sem Streamlit.
- `chat_pagina.py` (TP5): o chat com memória que as páginas mostram no fim (`chat_da_pagina`). O chat usa só a API (`POST /chat`); se ela não subir, mostra o comando para subi-la à mão.
- `assets/`: imagens usadas no painel.
- `pages/`: as páginas do menu (ver `pages/README.md`).

Para rodar: `.venv\Scripts\python.exe -m streamlit run Scripts/app.py`, da raiz do projeto; a API sobe junto (ver seção 5 do README da raiz).
