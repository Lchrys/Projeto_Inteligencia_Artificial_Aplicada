"""Sobe o projeto inteiro: prepara o ambiente, confere o modelo, sobe a API e o painel.

Rodar, na pasta do projeto:
    python iniciar.py

Na primeira vez, cria o ambiente .venv e instala as dependências. Depois, só confere o
modelo (que já está no cache) e sobe a API em outra janela e o painel nesta.
Para parar: feche a janela do painel (esta) e a janela da API.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENV = RAIZ / ".venv"
PYTHON_DO_VENV = VENV / "Scripts" / "python.exe"


def passo(titulo: str) -> None:
    print(f"\n== {titulo}")


def rodar(argumentos: list[str]) -> None:
    subprocess.run([str(PYTHON_DO_VENV), *argumentos], cwd=RAIZ, check=True)


def main() -> None:
    if not PYTHON_DO_VENV.exists():
        passo("Criando o ambiente .venv")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], cwd=RAIZ, check=True)
        passo("Instalando as dependências (demora na primeira vez)")
        rodar(["-m", "pip", "install", "-r", "requirements.txt"])

    passo("Conferindo o modelo de linguagem (baixa só na primeira vez)")
    rodar(["Code/modeling/baixar_modelo.py"])

    passo("Subindo a API em outra janela")
    subprocess.Popen(
        [str(PYTHON_DO_VENV), "-m", "uvicorn", "Code.api.main:app"],
        cwd=RAIZ,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    passo("Subindo o painel (http://localhost:8501)")
    # headless: pula a tela de boas-vindas do Streamlit, que pede e-mail na primeira execução.
    rodar(["-m", "streamlit", "run", "Scripts/app.py", "--server.headless", "true"])


if __name__ == "__main__":
    main()
