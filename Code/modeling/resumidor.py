"""Carrega o modelo de linguagem local e gera resumos em português.

Modelo padrão: Qwen/Qwen3-0.6B, baixado por Code/modeling/baixar_modelo.py.
A variável de ambiente MODELO_RESUMO troca o modelo (usada nas medições e nos testes).
Carregado com local_files_only=True: nunca baixa nada. Roda na CPU, em float32.

Geração determinística (sem amostragem), para a mesma entrada dar sempre a mesma saída.
"""

import os
import re
import time
from dataclasses import dataclass

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELO = os.environ.get("MODELO_RESUMO", "Qwen/Qwen3-0.6B")
MAX_NOVOS_TOKENS = 200

INSTRUCAO = (
    "Você resume textos sobre a indústria e o desenvolvimento econômico do Brasil. "
    "Escreva o resumo em português, em até três frases, usando apenas informações do texto. "
    "Copie os números exatamente como aparecem no texto e não acrescente dados novos. "
    "Ignore códigos de classificação (como JEL), referências e metadados do artigo: "
    "resuma só o conteúdo do texto."
)

ROTULO_INICIAL = re.compile(r"^\s*resumo\s*:\s*", re.IGNORECASE)


@dataclass
class Resumidor:
    nome: str
    tokenizador: AutoTokenizer
    modelo: AutoModelForCausalLM
    segundos_para_carregar: float


def carregar(nome: str = MODELO) -> Resumidor:
    """Lê os pesos do disco para a memória. Faz isso uma vez, na subida da API."""
    inicio = time.perf_counter()
    tokenizador = AutoTokenizer.from_pretrained(nome, local_files_only=True)
    modelo = AutoModelForCausalLM.from_pretrained(
        nome, local_files_only=True, dtype=torch.float32
    )
    modelo.eval()
    return Resumidor(nome, tokenizador, modelo, round(time.perf_counter() - inicio, 1))


def resumir(texto: str, resumidor: Resumidor) -> str:
    mensagens = [
        {"role": "system", "content": INSTRUCAO},
        {"role": "user", "content": f"Texto:\n{texto}\n\nResumo:"},
    ]
    # enable_thinking=False desliga o modo de raciocínio do Qwen3; os modelos Qwen2.5 ignoram o parâmetro.
    entrada = resumidor.tokenizador.apply_chat_template(
        mensagens,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
        enable_thinking=False,
    )
    with torch.no_grad():
        saida = resumidor.modelo.generate(
            **entrada,
            max_new_tokens=MAX_NOVOS_TOKENS,
            do_sample=False,
        )
    novos = saida[0, entrada["input_ids"].shape[1]:]
    texto_gerado = resumidor.tokenizador.decode(novos, skip_special_tokens=True).strip()
    return ROTULO_INICIAL.sub("", texto_gerado).strip()
