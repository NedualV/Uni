from datetime import date
from pathlib import Path

from app.models import Cliente, Empresa, Factura, ItemFactura
from app.pdf_generator import generar_pdf


def test_generar_pdf_crea_archivo(tmp_path: Path):
    factura = Factura(
        numero="000042",
        fecha=date(2026, 3, 15),
        empresa=Empresa(nombre="Empresa Demo", direccion="Calle Falsa 123", rnc="1-23-45678-9"),
        cliente=Cliente(nombre="Cliente Demo", rnc_cedula="001-1234567-8"),
        items=[
            ItemFactura(descripcion="Consultoría", cantidad=5, precio_unitario=1200),
            ItemFactura(descripcion="Soporte técnico", cantidad=1, precio_unitario=800),
        ],
        impuesto_pct=18,
        ncf="B0100000001",
        notas="Pago dentro de los 15 días siguientes a la emisión.",
    )

    destino = tmp_path / "factura.pdf"
    ruta = generar_pdf(factura, destino)

    assert ruta == destino
    assert ruta.is_file()
    assert ruta.stat().st_size > 0
    assert ruta.read_bytes().startswith(b"%PDF")
