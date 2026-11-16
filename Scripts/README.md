# Scripts (painel Streamlit)

Este README foi redigido com apoio de IA (Claude Opus 5.5 e Claude Haiku 5.5) e revisado pelo autor.

Objetivo: o painel que o usuário vê. Cada arquivo tem um papel:

- `app.py`: ponto de entrada do painel e página Início.
- `nucleo.py`: carga e cálculo das séries, sem Streamlit. Usado pelo painel e pela API.
- `dados.py`: funções de carga com cache do Streamlit, em volta de `nucleo.py`.
- `cliente_api.py`: chama a API local; se ela não responder, o painel lê direto de `nucleo.py`.
- `interface.py`: avisos, métricas, gráficos e botões de download comuns às páginas.
- `assets/`: imagens usadas no painel.
- `pages/`: as páginas do menu (ver `pages/README.md`).

Para rodar: `.venv\Scripts\python.exe -m streamlit run Scripts/app.py`, da raiz do projeto (ver seção 5 do README da raiz).
