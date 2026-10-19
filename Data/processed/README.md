# Data / processed

Arquivos recebidos pela API FastAPI depois da validação, não séries oficiais
novas.

- `world_bank_envios/`: CSV do DataBank enviados por `POST /world-bank`, em
  formato longo, um arquivo por identificador (`{id}.csv`). A página
  Comparação internacional consulta esses envios em `GET /world-bank/{id}`.
  O diretório fica de fora do Git (`.gitignore`).
