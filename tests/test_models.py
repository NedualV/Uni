from datetime import date

from app.models import Cliente, Empresa, Factura, ItemFactura


def _factura_de_prueba(impuesto_pct: float = 18.0) -> Factura:
    return Factura(
        numero="000001",
        fecha=date(2026, 1, 1),
        empresa=Empresa(nombre="Mi Empresa"),
        cliente=Cliente(nombre="Un Cliente"),
        items=[
            ItemFactura(descripcion="Servicio A", cantidad=2, precio_unitario=500),
            ItemFactura(descripcion="Servicio B", cantidad=1, precio_unitario=250),
        ],
        impuesto_pct=impuesto_pct,
    )


def test_subtotal_item():
    item = ItemFactura(descripcion="X", cantidad=3, precio_unitario=100)
    assert item.subtotal == 300


def test_totales_factura():
    factura = _factura_de_prueba(impuesto_pct=18.0)
    assert factura.subtotal == 1250
    assert factura.impuesto == 225.0
    assert factura.total == 1475.0


def test_totales_sin_impuesto():
    factura = _factura_de_prueba(impuesto_pct=0)
    assert factura.impuesto == 0
    assert factura.total == factura.subtotal


def test_factura_sin_items():
    factura = _factura_de_prueba()
    factura.items = []
    assert factura.subtotal == 0
    assert factura.total == 0
