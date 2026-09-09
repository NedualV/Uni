"""Interfaz gráfica (Tkinter) del Generador de Facturas."""
from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

from app import storage
from app.models import Cliente, Empresa, Factura, ItemFactura
from app.pdf_generator import generar_pdf

PADDING = 8


class GeneradorFacturasApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Generador de Facturas")
        self.geometry("880x720")
        self.minsize(760, 620)

        self.items: list[ItemFactura] = []

        self._crear_menu()
        self._crear_widgets()
        self._cargar_empresa_guardada()

    # ------------------------------------------------------------------ UI
    def _crear_menu(self) -> None:
        menu = tk.Menu(self)
        menu_archivo = tk.Menu(menu, tearoff=0)
        menu_archivo.add_command(label="Guardar datos de empresa", command=self._guardar_empresa_manual)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.destroy)
        menu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ayuda = tk.Menu(menu, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self._mostrar_acerca_de)
        menu.add_cascade(label="Ayuda", menu=menu_ayuda)
        self.config(menu=menu)

    def _crear_widgets(self) -> None:
        contenedor = ttk.Frame(self, padding=PADDING)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)

        self._crear_seccion_empresa(contenedor).grid(row=0, column=0, sticky="nsew", padx=(0, PADDING))
        self._crear_seccion_cliente(contenedor).grid(row=0, column=1, sticky="nsew")
        self._crear_seccion_meta(contenedor).grid(row=1, column=0, columnspan=2, sticky="ew", pady=PADDING)
        self._crear_seccion_items(contenedor).grid(row=2, column=0, columnspan=2, sticky="nsew")
        self._crear_seccion_notas(contenedor).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(PADDING, 0))
        self._crear_barra_totales(contenedor).grid(row=4, column=0, columnspan=2, sticky="ew", pady=PADDING)
        self._crear_boton_generar(contenedor).grid(row=5, column=0, columnspan=2, sticky="e")

        contenedor.rowconfigure(2, weight=1)

    def _crear_seccion_empresa(self, padre: ttk.Frame) -> ttk.LabelFrame:
        marco = ttk.LabelFrame(padre, text="Datos de la empresa", padding=PADDING)
        marco.columnconfigure(1, weight=1)

        self.var_empresa_nombre = tk.StringVar()
        self.var_empresa_direccion = tk.StringVar()
        self.var_empresa_telefono = tk.StringVar()
        self.var_empresa_email = tk.StringVar()
        self.var_empresa_rnc = tk.StringVar()
        self.var_empresa_logo = tk.StringVar()

        self._fila_entrada(marco, 0, "Nombre *", self.var_empresa_nombre)
        self._fila_entrada(marco, 1, "Dirección", self.var_empresa_direccion)
        self._fila_entrada(marco, 2, "Teléfono", self.var_empresa_telefono)
        self._fila_entrada(marco, 3, "Email", self.var_empresa_email)
        self._fila_entrada(marco, 4, "RNC", self.var_empresa_rnc)

        ttk.Label(marco, text="Logo").grid(row=5, column=0, sticky="w", pady=2)
        fila_logo = ttk.Frame(marco)
        fila_logo.grid(row=5, column=1, sticky="ew", pady=2)
        fila_logo.columnconfigure(0, weight=1)
        ttk.Entry(fila_logo, textvariable=self.var_empresa_logo).grid(row=0, column=0, sticky="ew")
        ttk.Button(fila_logo, text="Examinar…", command=self._elegir_logo).grid(row=0, column=1, padx=(4, 0))

        return marco

    def _crear_seccion_cliente(self, padre: ttk.Frame) -> ttk.LabelFrame:
        marco = ttk.LabelFrame(padre, text="Datos del cliente", padding=PADDING)
        marco.columnconfigure(1, weight=1)

        self.var_cliente_nombre = tk.StringVar()
        self.var_cliente_direccion = tk.StringVar()
        self.var_cliente_telefono = tk.StringVar()
        self.var_cliente_rnc = tk.StringVar()

        self._fila_entrada(marco, 0, "Nombre *", self.var_cliente_nombre)
        self._fila_entrada(marco, 1, "Dirección", self.var_cliente_direccion)
        self._fila_entrada(marco, 2, "Teléfono", self.var_cliente_telefono)
        self._fila_entrada(marco, 3, "RNC/Cédula", self.var_cliente_rnc)

        return marco

    def _crear_seccion_meta(self, padre: ttk.Frame) -> ttk.LabelFrame:
        marco = ttk.LabelFrame(padre, text="Datos de la factura", padding=PADDING)
        for col in range(6):
            marco.columnconfigure(col, weight=1)

        self.var_numero = tk.StringVar(value=storage.obtener_siguiente_numero())
        self.var_fecha = tk.StringVar(value=date.today().isoformat())
        self.var_ncf = tk.StringVar()
        self.var_impuesto = tk.StringVar(value="18")

        ttk.Label(marco, text="No. Factura").grid(row=0, column=0, sticky="w")
        ttk.Entry(marco, textvariable=self.var_numero, width=12).grid(row=0, column=1, sticky="ew", padx=(0, 12))

        ttk.Label(marco, text="Fecha (AAAA-MM-DD)").grid(row=0, column=2, sticky="w")
        ttk.Entry(marco, textvariable=self.var_fecha, width=14).grid(row=0, column=3, sticky="ew", padx=(0, 12))

        ttk.Label(marco, text="NCF (opcional)").grid(row=0, column=4, sticky="w")
        ttk.Entry(marco, textvariable=self.var_ncf, width=16).grid(row=0, column=5, sticky="ew")

        ttk.Label(marco, text="ITBIS %").grid(row=1, column=0, sticky="w", pady=(6, 0))
        entry_impuesto = ttk.Entry(marco, textvariable=self.var_impuesto, width=12)
        entry_impuesto.grid(row=1, column=1, sticky="ew", pady=(6, 0))
        entry_impuesto.bind("<KeyRelease>", lambda _e: self._actualizar_totales())

        return marco

    def _crear_seccion_items(self, padre: ttk.Frame) -> ttk.LabelFrame:
        marco = ttk.LabelFrame(padre, text="Servicios / Productos", padding=PADDING)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)

        fila_entrada = ttk.Frame(marco)
        fila_entrada.grid(row=0, column=0, sticky="ew", pady=(0, PADDING))
        fila_entrada.columnconfigure(0, weight=3)
        fila_entrada.columnconfigure(1, weight=1)
        fila_entrada.columnconfigure(2, weight=1)

        self.var_item_descripcion = tk.StringVar()
        self.var_item_cantidad = tk.StringVar(value="1")
        self.var_item_precio = tk.StringVar()

        ttk.Entry(fila_entrada, textvariable=self.var_item_descripcion).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Entry(fila_entrada, textvariable=self.var_item_cantidad, width=8).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Entry(fila_entrada, textvariable=self.var_item_precio, width=10).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(fila_entrada, text="Agregar", command=self._agregar_item).grid(row=0, column=3, padx=(4, 0))

        columnas = ("descripcion", "cantidad", "precio", "subtotal")
        self.tabla_items = ttk.Treeview(marco, columns=columnas, show="headings", height=8)
        for col, texto, ancho in (
            ("descripcion", "Descripción", 320),
            ("cantidad", "Cantidad", 90),
            ("precio", "Precio unitario", 130),
            ("subtotal", "Subtotal", 130),
        ):
            self.tabla_items.heading(col, text=texto)
            self.tabla_items.column(col, width=ancho, anchor="w" if col == "descripcion" else "e")
        self.tabla_items.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(marco, orient="vertical", command=self.tabla_items.yview)
        self.tabla_items.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        ttk.Button(marco, text="Eliminar seleccionado", command=self._eliminar_item).grid(
            row=2, column=0, sticky="w", pady=(PADDING, 0)
        )

        return marco

    def _crear_seccion_notas(self, padre: ttk.Frame) -> ttk.LabelFrame:
        marco = ttk.LabelFrame(padre, text="Notas / Condiciones", padding=PADDING)
        marco.columnconfigure(0, weight=1)
        self.texto_notas = tk.Text(marco, height=3, wrap="word")
        self.texto_notas.grid(row=0, column=0, sticky="ew")
        return marco

    def _crear_barra_totales(self, padre: ttk.Frame) -> ttk.Frame:
        marco = ttk.Frame(padre)
        marco.columnconfigure(0, weight=1)
        self.label_totales = ttk.Label(
            marco, text="Subtotal: RD$ 0.00    ITBIS: RD$ 0.00    Total: RD$ 0.00",
            font=("TkDefaultFont", 11, "bold"), anchor="e",
        )
        self.label_totales.grid(row=0, column=0, sticky="e")
        return marco

    def _crear_boton_generar(self, padre: ttk.Frame) -> ttk.Frame:
        marco = ttk.Frame(padre)
        ttk.Button(marco, text="Generar Factura (PDF)", command=self._generar_factura).pack()
        return marco

    def _fila_entrada(self, marco: ttk.Frame, fila: int, etiqueta: str, variable: tk.StringVar) -> None:
        ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=2)
        ttk.Entry(marco, textvariable=variable).grid(row=fila, column=1, sticky="ew", pady=2)

    # ------------------------------------------------------------- acciones
    def _cargar_empresa_guardada(self) -> None:
        empresa = storage.cargar_empresa()
        if empresa is None:
            return
        self.var_empresa_nombre.set(empresa.nombre)
        self.var_empresa_direccion.set(empresa.direccion)
        self.var_empresa_telefono.set(empresa.telefono)
        self.var_empresa_email.set(empresa.email)
        self.var_empresa_rnc.set(empresa.rnc)
        self.var_empresa_logo.set(empresa.logo_path)

    def _empresa_desde_formulario(self) -> Empresa:
        return Empresa(
            nombre=self.var_empresa_nombre.get().strip(),
            direccion=self.var_empresa_direccion.get().strip(),
            telefono=self.var_empresa_telefono.get().strip(),
            email=self.var_empresa_email.get().strip(),
            rnc=self.var_empresa_rnc.get().strip(),
            logo_path=self.var_empresa_logo.get().strip(),
        )

    def _guardar_empresa_manual(self) -> None:
        empresa = self._empresa_desde_formulario()
        if not empresa.nombre:
            messagebox.showwarning("Datos incompletos", "Ingresa al menos el nombre de la empresa.")
            return
        storage.guardar_empresa(empresa)
        messagebox.showinfo("Guardado", "Los datos de la empresa se guardaron como predeterminados.")

    def _elegir_logo(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Selecciona el logo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.var_empresa_logo.set(ruta)

    def _agregar_item(self) -> None:
        descripcion = self.var_item_descripcion.get().strip()
        if not descripcion:
            messagebox.showwarning("Dato faltante", "Escribe una descripción para el ítem.")
            return
        try:
            cantidad = float(self.var_item_cantidad.get().replace(",", "."))
            precio = float(self.var_item_precio.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Valor inválido", "Cantidad y precio unitario deben ser números.")
            return
        if cantidad <= 0 or precio < 0:
            messagebox.showerror("Valor inválido", "La cantidad debe ser mayor a 0 y el precio no puede ser negativo.")
            return

        item = ItemFactura(descripcion=descripcion, cantidad=cantidad, precio_unitario=precio)
        self.items.append(item)
        self.tabla_items.insert(
            "", "end",
            values=(item.descripcion, f"{item.cantidad:g}", f"{item.precio_unitario:,.2f}", f"{item.subtotal:,.2f}"),
        )

        self.var_item_descripcion.set("")
        self.var_item_cantidad.set("1")
        self.var_item_precio.set("")
        self._actualizar_totales()

    def _eliminar_item(self) -> None:
        seleccion = self.tabla_items.selection()
        if not seleccion:
            return
        for iid in seleccion:
            indice = self.tabla_items.index(iid)
            del self.items[indice]
            self.tabla_items.delete(iid)
        self._actualizar_totales()

    def _impuesto_pct(self) -> float:
        try:
            return float(self.var_impuesto.get().replace(",", "."))
        except ValueError:
            return 0.0

    def _actualizar_totales(self) -> None:
        subtotal = round(sum(item.subtotal for item in self.items), 2)
        impuesto_pct = self._impuesto_pct()
        impuesto = round(subtotal * impuesto_pct / 100, 2)
        total = subtotal + impuesto
        self.label_totales.configure(
            text=f"Subtotal: RD$ {subtotal:,.2f}    ITBIS: RD$ {impuesto:,.2f}    Total: RD$ {total:,.2f}"
        )

    def _generar_factura(self) -> None:
        empresa = self._empresa_desde_formulario()
        cliente = Cliente(
            nombre=self.var_cliente_nombre.get().strip(),
            direccion=self.var_cliente_direccion.get().strip(),
            telefono=self.var_cliente_telefono.get().strip(),
            rnc_cedula=self.var_cliente_rnc.get().strip(),
        )

        errores = []
        if not empresa.nombre:
            errores.append("El nombre de la empresa es obligatorio.")
        if not cliente.nombre:
            errores.append("El nombre del cliente es obligatorio.")
        if not self.items:
            errores.append("Agrega al menos un producto o servicio.")

        try:
            fecha = date.fromisoformat(self.var_fecha.get().strip())
        except ValueError:
            errores.append("La fecha debe tener el formato AAAA-MM-DD.")
            fecha = date.today()

        numero = self.var_numero.get().strip()
        if not numero:
            errores.append("El número de factura es obligatorio.")

        if errores:
            messagebox.showerror("Revisa el formulario", "\n".join(f"• {e}" for e in errores))
            return

        factura = Factura(
            numero=numero,
            fecha=fecha,
            empresa=empresa,
            cliente=cliente,
            items=list(self.items),
            impuesto_pct=self._impuesto_pct(),
            ncf=self.var_ncf.get().strip(),
            notas=self.texto_notas.get("1.0", "end").strip(),
        )

        destino = filedialog.asksaveasfilename(
            title="Guardar factura",
            defaultextension=".pdf",
            initialfile=f"Factura_{factura.numero}.pdf",
            filetypes=[("Documento PDF", "*.pdf")],
        )
        if not destino:
            return

        try:
            ruta = generar_pdf(factura, Path(destino))
        except Exception as exc:  # noqa: BLE001 - se informa al usuario cualquier fallo de generación
            messagebox.showerror("Error al generar la factura", str(exc))
            return

        storage.guardar_empresa(empresa)
        storage.confirmar_numero(factura.numero)

        if messagebox.askyesno("Factura generada", f"Factura guardada en:\n{ruta}\n\n¿Deseas abrirla ahora?"):
            self._abrir_archivo(ruta)

        self._reiniciar_formulario_factura()

    def _reiniciar_formulario_factura(self) -> None:
        self.items.clear()
        for fila in self.tabla_items.get_children():
            self.tabla_items.delete(fila)
        self.var_numero.set(storage.obtener_siguiente_numero())
        self.var_ncf.set("")
        self.texto_notas.delete("1.0", "end")
        self._actualizar_totales()

    @staticmethod
    def _abrir_archivo(ruta: Path) -> None:
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["cmd", "/c", "start", "", str(ruta)], shell=False)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(ruta)])
            else:
                subprocess.Popen(["xdg-open", str(ruta)])
        except Exception:
            pass

    def _mostrar_acerca_de(self) -> None:
        messagebox.showinfo(
            "Acerca de",
            "Generador de Facturas\nCrea facturas profesionales en PDF de forma rápida y sencilla.",
        )


def main() -> None:
    app = GeneradorFacturasApp()
    app.mainloop()


if __name__ == "__main__":
    main()
