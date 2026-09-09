"""Modelos de datos para la generación de facturas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Empresa:
    nombre: str
    direccion: str = ""
    telefono: str = ""
    email: str = ""
    rnc: str = ""
    logo_path: str = ""


@dataclass
class Cliente:
    nombre: str
    direccion: str = ""
    telefono: str = ""
    rnc_cedula: str = ""


@dataclass
class ItemFactura:
    descripcion: str
    cantidad: float
    precio_unitario: float

    @property
    def subtotal(self) -> float:
        return round(self.cantidad * self.precio_unitario, 2)


@dataclass
class Factura:
    numero: str
    fecha: date
    empresa: Empresa
    cliente: Cliente
    items: list[ItemFactura] = field(default_factory=list)
    impuesto_pct: float = 18.0
    ncf: str = ""
    notas: str = ""

    @property
    def subtotal(self) -> float:
        return round(sum(item.subtotal for item in self.items), 2)

    @property
    def impuesto(self) -> float:
        return round(self.subtotal * (self.impuesto_pct / 100), 2)

    @property
    def total(self) -> float:
        return round(self.subtotal + self.impuesto, 2)
