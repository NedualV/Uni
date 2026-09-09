from pathlib import Path

from app import storage
from app.models import Empresa


def test_guardar_y_cargar_empresa(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(storage, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(storage, "EMPRESA_FILE", tmp_path / "empresa.json")
    monkeypatch.setattr(storage, "CONTADOR_FILE", tmp_path / "contador.json")

    assert storage.cargar_empresa() is None

    empresa = Empresa(nombre="Mi Empresa", direccion="Aquí", rnc="123")
    storage.guardar_empresa(empresa)

    cargada = storage.cargar_empresa()
    assert cargada == empresa


def test_numeracion_correlativa(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(storage, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(storage, "EMPRESA_FILE", tmp_path / "empresa.json")
    monkeypatch.setattr(storage, "CONTADOR_FILE", tmp_path / "contador.json")

    assert storage.obtener_siguiente_numero() == "000001"

    storage.confirmar_numero("000001")
    assert storage.obtener_siguiente_numero() == "000002"

    storage.confirmar_numero("000010")
    assert storage.obtener_siguiente_numero() == "000011"
