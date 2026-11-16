# Testes da API

Objetivo: verificar as regras da API sem depender de rede nem de um modelo pesado,
e, quando pedido, confirmar a integração com o modelo real.

- `test_texto.py`: testes rápidos da rota `POST /processar_texto`, com modelo falso.
  Cobrem 422, 503, 502, 504, 500 e o formato da resposta 200. Rodam sempre.
- `test_modelo_real.py`: integração com o Qwen3-0.6B de verdade. Demora cerca de um
  minuto e só roda com `RODAR_MODELO_REAL=1`.

Comandos, da raiz do projeto:

```
python -m unittest discover -s Code/api/tests -t .
RODAR_MODELO_REAL=1 python -m unittest Code.api.tests.test_modelo_real -v
```

Detalhes e a justificativa do teste com modelo real estão em `Code/api/README.md`.
