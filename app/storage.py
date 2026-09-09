"""Persistencia local: perfil de empresa y numeración correlativa de facturas."""
from __future__ import annotations

import json
from pathlib import Path

from app.models import Empresa

CONFIG_DIR = Path.home() / ".generador_facturas"
EMPRESA_FILE = CONFIG_DIR / "empresa.json"
CONTADOR_FILE = CONFIG_DIR / "contador.json"


def _asegurar_directorio() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def cargar_empresa() -> Empresa | None:
    """Carga el perfil de empresa guardado previamente, si existe."""
    if not EMPRESA_FILE.exists():
        return None
    try:
        data = json.loads(EMPRESA_FILE.read_text(encoding="utf-8"))
        return Empresa(**data)
    except (json.JSONDecodeError, TypeError):
        return None


def guardar_empresa(empresa: Empresa) -> None:
    """Guarda el perfil de empresa para reutilizarlo en próximas facturas."""
    _asegurar_directorio()
    EMPRESA_FILE.write_text(
        json.dumps(empresa.__dict__, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def obtener_siguiente_numero() -> str:
    """Devuelve el próximo número de factura (sin reservarlo todavía)."""
    contador = 0
    if CONTADOR_FILE.exists():
        try:
            contador = json.loads(CONTADOR_FILE.read_text(encoding="utf-8")).get("contador", 0)
        except json.JSONDecodeError:
            contador = 0
    return f"{contador + 1:06d}"


def confirmar_numero(numero_texto: str) -> None:
    """Reserva un número de factura como usado, si es numérico correlativo."""
    if not numero_texto.isdigit():
        return
    _asegurar_directorio()
    actual = 0
    if CONTADOR_FILE.exists():
        try:
            actual = json.loads(CONTADOR_FILE.read_text(encoding="utf-8")).get("contador", 0)
        except json.JSONDecodeError:
            actual = 0
    nuevo = max(actual, int(numero_texto))
    CONTADOR_FILE.write_text(json.dumps({"contador": nuevo}), encoding="utf-8")
