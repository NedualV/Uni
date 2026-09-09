"""Instala las dependencias necesarias (si faltan) y ejecuta la aplicación."""
import subprocess
import sys


def install_requirements() -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def run_program() -> None:
    from app.gui import main

    main()


if __name__ == "__main__":
    try:
        import reportlab  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:
        install_requirements()
    run_program()
