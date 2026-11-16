"""Baixa o modelo de linguagem uma vez, com internet, antes de subir a API.

Modelo padrão: Qwen/Qwen3-0.6B (Apache 2.0, sem gated), cerca de 1,5 GB em disco.
Outro modelo pode ser baixado com a variável MODELO_RESUMO (ex.: Qwen/Qwen2.5-0.5B-Instruct).
Os pesos vão para o cache do Hugging Face (fora do projeto), e não para o Git.

A API só lê o que já está no disco: Code/modeling/resumidor.py carrega com
local_files_only=True, então nunca baixa nada na subida.

Rodar, da raiz do projeto, com o .venv ativo:
    python Code/modeling/baixar_modelo.py
"""

import os
import time

from huggingface_hub import snapshot_download

MODELO = os.environ.get("MODELO_RESUMO", "Qwen/Qwen3-0.6B")

# Só o que o Transformers usa: pesos, configuração e tokenizador.
ARQUIVOS = ["*.json", "*.safetensors", "*.txt", "tokenizer*", "merges.txt", "vocab.json"]


def main() -> None:
    print(f"Baixando {MODELO} (~3 GB na primeira vez; nas outras, só confere)...")
    inicio = time.perf_counter()
    pasta = snapshot_download(MODELO, allow_patterns=ARQUIVOS)
    print(f"Pronto em {time.perf_counter() - inicio:.0f} s.")
    print(f"Pasta do modelo: {pasta}")


if __name__ == "__main__":
    main()
