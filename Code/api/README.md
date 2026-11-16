# API do monitor (FastAPI)

API local para consultar as séries oficiais e os textos do ODS 9, e para
receber o CSV do DataBank. O painel consome estas rotas em Início, Série
histórica, Comparação internacional e Contexto ODS 9
(`Scripts/cliente_api.py`). Se o serviço não responder, as páginas leem
direto de `Scripts/nucleo.py`. O Streamlit Community Cloud não sobe esta API.

Organização (padrão da disciplina): `main.py` cria a aplicação;
`models.py` declara os modelos Pydantic de entrada e saída
(`response_model` em todas as rotas); `routers/` separa séries, ODS 9 e análise de texto.
A série do Ipeadata fica em cache de uma hora.

Documentação interativa gerada pelo FastAPI: http://127.0.0.1:8000/docs

## Como subir (Windows, na raiz do repositório)

```
.venv\Scripts\activate
uvicorn Code.api.main:app --reload
```

O serviço fica em http://127.0.0.1:8000. Em outro terminal, `streamlit run Scripts/app.py`.

A URL pode ser alterada no painel por `API_URL` em `.streamlit/secrets.toml`.
O padrão é `http://127.0.0.1:8000`.

## Rotas

### GET /saude

Confirma que a API está no ar. O painel consulta esta rota a cada 30 segundos
(cache). Resposta: `SaudeOut`.

```
curl http://127.0.0.1:8000/saude
```

### GET /serie/transformacao

Série SCN10_VAITY10 (Ipeadata), indicador 9.2.1. Recorte opcional por ano.
Consumida pela Série histórica e pelo gráfico da Início. Resposta: `SerieOut`.

```
curl "http://127.0.0.1:8000/serie/transformacao?inicio=1995&fim=2025"
```

### POST /world-bank

Recebe o CSV exportado do DataBank, valida o formato, converte para formato
longo e grava em `Data/processed/world_bank_envios/{id}.csv`. Sucesso
devolve 201 (`WorldBankEnvioOut`) com o identificador. Arquivo fora do
formato devolve 400. A Comparação internacional consome esta rota no upload.

```
curl -X POST http://127.0.0.1:8000/world-bank ^
  -F "arquivo=@Data/raw/world_bank_setorial.csv"
```

### GET /world-bank/{id}

Consulta um envio gravado pelo POST. Filtros opcionais por país (código
ISO3), indicador, início e fim. NV.IND.MANF.ZS é o indicador 9.2.1. Envio
inexistente devolve 404. Resposta: `WorldBankOut`.

```
curl "http://127.0.0.1:8000/world-bank/{id}?pais=BRA&indicador=NV.IND.MANF.ZS&inicio=1995"
```

### GET /ods9/metas e GET /ods9/metas/{codigo}

Metas extraídas da página ODS 9 do Ipea. Consumidas pela página Contexto ODS 9.
Respostas: `MetasOut` e `MetaDetalheOut`.

```
curl http://127.0.0.1:8000/ods9/metas
curl http://127.0.0.1:8000/ods9/metas/9.2
```

### GET /fatos/resumo

Indicadores já calculados (último valor, variação desde 1995, máximo e ranking).
O ranking é a posição do Brasil entre as economias do CSV de exemplo do
DataBank (`Data/raw/world_bank_setorial.csv`) no último ano com valor do
Brasil — não um ranking mundial. O JSON traz `universo`,
`paises_no_arquivo`, `paises_com_valor_no_ano`, `paises_sem_valor_no_ano` e
`nota`. A página Início consome esta rota. Ainda não é usado pelo modelo de
linguagem; num relatório futuro, o modelo só redigiria a partir deste JSON. Resposta: `FatosOut`.

```
curl http://127.0.0.1:8000/fatos/resumo
```

### POST /processar_texto

Gera um resumo em português com um modelo de linguagem **local**
(`Qwen/Qwen3-0.6B`, na CPU). O modelo é carregado uma vez, quando a API sobe;
se a carga falhar, a API sobe mesmo assim e esta rota responde 503. O resumo
foi gerado por modelo e precisa de revisão humana antes de ser usado como
fato. O campo `motor` diz qual modelo gerou o texto.

```
curl -X POST http://127.0.0.1:8000/processar_texto ^
  -H "Content-Type: application/json" ^
  -d "{\"texto\": \"A indústria de transformação perdeu participação no PIB...\"}"
```

**Entrada** (`PedidoTexto`): `texto`, de 50 a 2.000 caracteres (sem contar espaços
nas pontas), e `tipo_analise`, que hoje só aceita `"resumo"`. Campo a mais, texto
fora desse intervalo ou tipo diferente respondem **422**, com a lista de problemas.

**Saída** (`ResultadoResumo`, 200): `tipo_analise`, `texto` (o texto processado,
sem espaços nas pontas), `resumo`, `motor` e `aviso` (ressalva fixa: resumo
gerado por modelo, sujeito a revisão humana). Os modelos aparecem no `/docs`.

Tempo medido na máquina de
referência (Intel Core i5-1035G1, 8 GB de RAM, sem GPU): de 12 s a 38 s por
resumo, com mediana de 26 s.

## Ambiente do modelo de linguagem

Bibliotecas usadas pelo modelo de linguagem e pela API:
- `transformers`: carrega o tokenizador e o modelo do disco e gera o resumo.
- `torch`: executa o modelo (versão só de CPU).
- `huggingface_hub`: baixa o modelo do Hugging Face, uma vez.
- `psutil`: mede a memória do processo, só no script de medição.
- `httpx`: cliente que o `TestClient` do FastAPI usa, só nos testes.
- `fastapi` e `uvicorn`: a API e o servidor que a executa.

1. Instalar as dependências. O `requirements.txt` aponta o `torch` para a versão
   só de CPU do PyTorch (`--extra-index-url`), para o build no Streamlit Cloud
   não baixar a versão com CUDA.
   ```
   pip install -r requirements.txt
   ```
2. Baixar o modelo uma vez, com internet (cerca de 1,5 GB, fora do Git):
   ```
   python Code/modeling/baixar_modelo.py
   ```
3. Subir a API, da raiz do projeto:
   ```
   uvicorn Code.api.main:app --reload
   ```
   Com `--reload`, cada arquivo salvo recarrega o modelo. Para uso contínuo,
   rode sem `--reload`.

**Execução sem internet.** Com o modelo já baixado, a API carrega do disco. Para
confirmar que não há acesso à rede, subir com `HF_HUB_OFFLINE=1`: a API sobe e
responde normalmente.

**Ajustes para esta máquina.**
- **Precisão float32, na CPU.** Em float32, o modelo ocupa cerca de 2,4 GB de
  RAM, com 7,7 GB utilizáveis. O Qwen2.5-1.5B-Instruct ocupa cerca de 6,2 GB só
  nos pesos e travou a máquina sem terminar o primeiro texto. Por isso foi
  descartado (`Docs/Escolha_do_modelo.md`, seção 1).
- **Modo de raciocínio desligado.** O Qwen3 gera um raciocínio antes da
  resposta, e o resumo precisa só da resposta: a chamada usa
  `enable_thinking=False`.
- **Aviso do Windows sobre links simbólicos.** O cache do Hugging Face não usa
  links simbólicos sem o Modo de Desenvolvedor, e o download mostra um aviso.
  Não impede o uso; só pode ocupar mais espaço em disco.

**Códigos de erro de `POST /processar_texto`:**

| Código | Quando | O que o cliente vê |
|---|---|---|
| 422 | texto com menos de 50 ou mais de 2.000 caracteres, campo extra ou tipo de análise inválido | lista de problemas, um item por campo |
| 502 | o modelo devolveu um resumo vazio | frase em `detail` |
| 503 | o modelo não carregou quando a API subiu | frase em `detail`; as outras rotas seguem no ar |
| 504 | a geração passou de 120 s | frase em `detail` |
| 500 | erro inesperado | frase com um código de rastreio; o traceback só vai para o log da API |

Para informar um 500 a quem mantém a API, basta o código da mensagem: o log da
API mostra o mesmo código, junto do traceback completo.

**Limites conhecidos** (ver `Docs/Escolha_do_modelo.md`, seção 3):
- Textos em inglês podem gerar resumos que repetem o título.
- Já houve inversão de fato e troca de termo em resumos de teste. Por isso,
  nenhum resumo é exibido como fato sem revisão humana.
- Uma geração de cada vez. Se uma passar de 120 s, a rota responde 504, mas a
  geração continua até terminar, e o pedido seguinte espera por ela.

**Testes.** Rodar da raiz do projeto, com o `.venv` ativo ou com o Python do venv:
```
python -m unittest discover -s Code/api/tests -t .
```
Os testes usam um modelo falso e cobrem 422, 502, 503, 504, 500 e o formato da
resposta 200.

**Teste com o modelo real** (integração de fato; demora cerca de 1 minuto):
```
RODAR_MODELO_REAL=1 python -m unittest Code.api.tests.test_modelo_real -v
```
Carrega o Qwen3-0.6B como a API faz na subida, gera resumos de verdade e confere o
formato da resposta, o tamanho do resumo, o tempo e se os números do resumo estão no
texto de origem. Sem a variável, esses 4 testes são pulados.

## Onde ficam os códigos de erro

Os modelos de erro e o tratamento de erros inesperados estão em `Code/api/erros.py`.
A rota de texto (`Code/api/routers/texto.py`) declara os códigos 502, 503 e 504 no
`/docs`, e o 500 é declarado em toda a API.

## Variável MODELO_RESUMO

Troca o modelo de linguagem usado pela API e pelos scripts de `Code/modeling/`.
Sem a variável, o padrão é `Qwen/Qwen3-0.6B`.
