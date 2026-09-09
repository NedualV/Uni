# Generador de Facturas

Aplicación de escritorio en Python para crear facturas profesionales en PDF de forma rápida, pensada para freelancers y pequeños negocios en República Dominicana (aunque funciona para cualquier país).

![Generador de Facturas](https://github.com/user-attachments/assets/bb1fe839-9ee9-461e-a6f0-57381b49d500)

## Características

- **Múltiples productos/servicios por factura**, con tabla editable (agregar/quitar filas).
- **Numeración correlativa automática**, editable si necesitas un formato propio.
- **Perfil de empresa persistente**: escribe tus datos una vez y se recuerdan en la próxima factura.
- **Logo de empresa** opcional en el PDF.
- **ITBIS/impuesto configurable** (18% por defecto, editable) y cálculo automático de subtotal, impuesto y total.
- **Campo de NCF opcional** para comprobantes fiscales dominicanos.
- **Notas/condiciones de pago** libres al pie de la factura.
- **Diseño de PDF profesional**: encabezado con logo, bloque de "Facturar a", tabla de ítems y totales con estilo, pie de página.
- **Validación de datos** antes de generar el PDF (campos obligatorios, números válidos, fecha).
- Eliges dónde guardar cada PDF (ya no se fuerza al escritorio).

## Requisitos

- Python 3.9 o superior.
- Tkinter (incluido de serie en las instalaciones oficiales de Python para Windows/macOS; en Linux puede requerir instalar el paquete del sistema, p. ej. `sudo apt install python3-tk`).

## Instalación y ejecución

### Opción 1: script automático

```bash
python install_and_run.py
```

Este script instala las dependencias (`reportlab`, `Pillow`) si faltan y abre la aplicación.

### Opción 2: manual

```bash
pip install -r requirements.txt
python main.py
```

### Doble clic (Windows)

También puedes abrir `install_and_run.py` con doble clic desde el explorador de archivos.

## Uso

1. Completa los **datos de la empresa** (se guardan automáticamente para la próxima vez) y opcionalmente añade un logo.
2. Completa los **datos del cliente**.
3. Revisa el **número de factura**, la **fecha** y el **% de ITBIS**; agrega el **NCF** si aplica.
4. Añade cada **producto o servicio** con su cantidad y precio unitario a la tabla.
5. Agrega notas o condiciones de pago si lo necesitas.
6. Pulsa **"Generar Factura (PDF)"**, elige dónde guardarla y listo.

## Estructura del proyecto

```
Generador-de-Facturas/
├── main.py                  # Punto de entrada
├── install_and_run.py       # Instala dependencias y ejecuta la app
├── install_and_run.spec     # Configuración de PyInstaller para empaquetar un ejecutable
├── requirements.txt         # Dependencias de producción
├── requirements-dev.txt     # Dependencias para desarrollo/pruebas
├── app/
│   ├── models.py            # Entidades: Empresa, Cliente, ItemFactura, Factura
│   ├── storage.py           # Persistencia local (perfil de empresa, numeración)
│   ├── pdf_generator.py     # Generación del PDF con reportlab
│   └── gui.py                # Interfaz gráfica (Tkinter)
└── tests/                   # Pruebas automatizadas (pytest)
```

Los datos de la empresa y el contador de facturas se guardan en `~/.generador_facturas/` (fuera del repositorio).

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

## Generar un ejecutable (opcional)

Para distribuir la app como un `.exe`/binario independiente con [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller install_and_run.spec
```

El ejecutable resultante quedará en `dist/`.

## Licencia

Este proyecto se distribuye bajo la licencia [MIT](LICENSE).
