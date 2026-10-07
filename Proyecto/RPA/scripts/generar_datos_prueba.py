"""
Genera la estructura de carpetas DESORDENADA descrita en el enunciado (seccion RPA)
para probar el robot de UiPath.

- Carpetas: clientes, proveedores, reclamos, registro, productos + "guion y descripcion".
- Archivos Excel nombrados igual, con varias hojas. Solo interesan las hojas
  llamadas "clientes" y "productos" (pueden estar en cualquier carpeta/archivo).
- Incluye los archivos de ejemplo del auxiliar (Proyecto/Docs) tal cual.
- Incluye filas invalidas a proposito para probar el log de rechazados.

IMPORTANTE: se genera en una ruta CORTA (C:\\QuetzalMart_RPA\\Entrada) porque Excel no
abre archivos cuya ruta completa supera ~218 caracteres y la carpeta del repo (OneDrive)
ya es muy larga. Ademas se deja una copia comprimida en Proyecto/RPA/DatosPrueba.zip.

Uso:
    python generar_datos_prueba.py            # genera en C:\\QuetzalMart_RPA\\Entrada
    python generar_datos_prueba.py C:\\ruta    # genera en otra ruta
"""
import shutil
import sys
from pathlib import Path

import openpyxl
import xlwt

BASE = Path(__file__).resolve().parent.parent          # Proyecto/RPA
DOCS = BASE.parent / "Docs"                            # Proyecto/Docs
DESTINO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\QuetzalMart_RPA\Entrada")
RAIZ = DESTINO / "QuetzalMart - Ventas"

COLS_CLI = ["Name*", "Company Type*", "Related Company", "Email", "Phone", "Street",
            "Street2", "City", "State", "Zip", "Country", "Tax ID", "Website", "Tags",
            "Reference", "Notes"]
COLS_PRO = ["External ID", "Name", "Product Type", "Internal Reference", "Barcode",
            "Sales Price", "Cost", "Weight", "Sales Description", "Product Values",
            "Cantidad a la mano", "Está publicado"]


def cli(name, ctype, related="", email="", phone="", street="", street2="", city="",
        state="", zip_="", country="", vat="", web="", tags="", ref="", notes=""):
    return [name, ctype, related, email, phone, street, street2, city, state, zip_,
            country, vat, web, tags, ref, notes]


def pro(ext, name, ptype, ref="", barcode="", price="", cost="", weight="", desc="",
        values="", qty="", pub=""):
    return [ext, name, ptype, ref, barcode, price, cost, weight, desc, values, qty, pub]


# ----------------------------------------------------------------------------- datos
CLIENTES_CENTRAL = [
    cli("Abarrotería La Bendición", "Company", email="compras@labendicion.gt",
        phone="+502 2251 4410", street="6a Avenida 12-45 Zona 1", city="Guatemala",
        zip_="01001", country="GT", vat="4589632-1", ref="QM-CLI-001",
        notes="Cliente mayorista sucursal central"),
    cli("María José Castillo", "Person", related="Abarrotería La Bendición",
        email="mjcastillo@labendicion.gt", phone="+502 5512 7788", city="Guatemala",
        country="GT", ref="QM-CLI-002"),
    cli("Supermercado El Ahorro", "Company", email="gerencia@elahorro.com.gt",
        phone="+502 7765 1200", street="Calzada Roosevelt 22-43 Zona 11",
        city="Mixco", zip_="01057", country="GT", vat="7812345-6",
        web="https://elahorro.com.gt", ref="QM-CLI-003"),
    cli("Carlos Enrique Pérez", "Person", email="carlos.perez@gmail.com",
        phone="+502 4021 3399", street="Km 14.5 Carretera a El Salvador",
        city="Santa Catarina Pinula", country="GT", ref="QM-CLI-004"),
    cli("Tienda Doña Tere", "Company", email="donatere@hotmail.com",
        phone="+502 7832 0045", street="3a Calle 4-10 Zona 2", city="Antigua Guatemala",
        country="GT", ref="QM-CLI-005"),
    cli("Ana Lucía Morales", "Person", email="ana.morales@outlook.com",
        phone="+502 3344 5566", city="Quetzaltenango", country="GT", ref="QM-CLI-006"),
    # ---- filas invalidas (deben ir al log) ----
    cli("", "Person", email="sin.nombre@correo.com", city="Guatemala", country="GT"),
    cli("Pedro Sin Tipo", "", email="pedro@correo.com", city="Escuintla", country="GT"),
    cli("Luis Correo Malo", "Person", email="luis.correo-malo.com", city="Cobán",
        country="GT"),
    cli("", "", ""),  # fila completamente vacia (se ignora sin log)
]

CLIENTES_RECLAMOS = [
    cli("Distribuidora Azteca S.A. de C.V.", "Company", email="contacto@azteca.mx",
        phone="+52 33 3615 2200", street="Av. Juárez 1450", city="Guadalajara",
        state="Jalisco", zip_="44100", country="MX", vat="DAZ010203AB1",
        ref="QM-MX-001", notes="Sucursal México"),
    cli("Fernanda Ríos", "Person", related="Distribuidora Azteca S.A. de C.V.",
        email="fernanda.rios@azteca.mx", phone="+52 33 1234 5678", city="Guadalajara",
        country="MX", ref="QM-MX-002"),
    cli("Pupusería El Comalito", "Company", email="elcomalito@gmail.com",
        phone="+503 2222 8899", street="Boulevard de los Héroes 1020",
        city="San Salvador", country="SV", ref="QM-SV-001", notes="Sucursal El Salvador"),
    cli("José Roberto Hernández", "Person", email="jrhernandez@yahoo.com",
        phone="+503 7788 1122", city="Santa Ana", country="SV", ref="QM-SV-002"),
    cli("Cliente Tipo Raro", "Empresa Grande", email="raro@correo.com", country="SV"),
]

CLIENTES_REGISTRO = [
    cli("Minisuper Los Altos", "Company", email="losaltos@minisuper.gt",
        phone="+502 7761 4455", city="Totonicapán", country="GT", ref="QM-CLI-007"),
    cli("Sofía Alejandra Juárez", "Person", email="sofia.juarez@gmail.com",
        phone="+502 5900 1234", city="Huehuetenango", country="GT", ref="QM-CLI-008"),
    # duplicado exacto de un cliente de otro archivo -> rechazado por duplicado
    cli("Carlos Enrique Pérez", "Person", email="carlos.perez@gmail.com",
        phone="+502 4021 3399", city="Santa Catarina Pinula", country="GT"),
]

PRODUCTOS_BEBIDAS = [
    pro("QM_BEB_001", "Agua Pura Salvavidas 600 ml", "Goods", "QM-BEB-001",
        "7401005100018", 5.0, 2.75, 0.62, "Agua purificada, botella 600 ml", "", 240, True),
    pro("QM_BEB_002", "Gaseosa Cola 3 L", "Goods", "QM-BEB-002", "7401005100025",
        22.5, 15.0, 3.1, "Bebida carbonatada sabor cola 3 litros", "", 120, True),
    pro("QM_BEB_003", "Café Quetzal Molido 454 g", "Goods", "QM-BEB-003",
        "7401005100032", 48.0, 31.0, 0.48, "Café 100% guatemalteco, tueste oscuro", "",
        85, True),
    pro("QM_BEB_004", "Jugo de Naranja Natural 1 L", "Goods", "QM-BEB-004",
        "7401005100049", 18.0, 11.5, 1.05, "Jugo natural sin azúcar añadida", "", 60,
        False),
    pro("QM_BEB_005", "Horchata en Polvo 400 g", "Goods", "QM-BEB-005",
        "7401005100056", 16.5, 9.0, 0.4, "Bebida tradicional de arroz y canela", "", 0,
        True),
]

PRODUCTOS_ABARROTES = [
    pro("QM_ABA_001", "Frijol Negro Volteado 400 g", "Goods", "QM-ABA-001",
        "7401005200015", 12.0, 7.25, 0.42, "Frijol negro volteado listo para servir", "",
        150, True),
    pro("QM_ABA_002", "Arroz Blanco Premium 2 lb", "Goods", "QM-ABA-002",
        "7401005200022", 11.0, 6.8, 0.91, "Arroz grano largo 2 libras", "", 200, True),
    pro("QM_ABA_003", "Tortillas de Maíz (paquete 30)", "Goods", "QM-ABA-003",
        "7401005200039", 10.0, 6.0, 0.9, "Tortillas frescas de maíz amarillo", "", 90,
        True),
    pro("QM_ABA_004", "Aceite Vegetal 900 ml", "Goods", "QM-ABA-004", "7401005200046",
        27.0, 19.5, 0.85, "Aceite vegetal comestible", "", 75, False),
    pro("QM_SER_001", "Entrega a Domicilio QuetzalMart", "Service", "QM-SER-001", "",
        25.0, 12.0, "", "Servicio de entrega en zona urbana", "", "", True),
    # ---- filas invalidas ----
    pro("", "Producto Sin ID Externo", "Goods", "QM-ABA-090", "", 10, 5, "", "", "", 5,
        True),
    pro("QM_ABA_091", "", "Goods", "QM-ABA-091", "", 10, 5, "", "", "", 5, True),
    pro("QM_ABA_092", "Azúcar Morena 5 lb", "Goods", "QM-ABA-092", "", "doce", 20, "",
        "", "", 10, True),
    pro("QM_ABA_093", "Sal Yodada 1 kg", "Goods", "QM-ABA-093", "", 4.5, 2, "", "", "",
        -15, True),
    pro("QM_ABA_094", "Harina de Trigo 1 lb", "Electrónico", "QM-ABA-094", "", 6, 3,
        "", "", "", 40, True),
    pro("QM_ABA_095", "Pasta Spaghetti 200 g", "Goods", "QM-ABA-095", "", 5, 2.5, "",
        "", "", 30, "tal vez"),
]

PRODUCTOS_PROVEEDOR = [
    pro("QM_LIM_001", "Detergente en Polvo 1 kg", "Goods", "QM-LIM-001",
        "7401005300012", 32.0, 22.0, 1.0, "Detergente multiusos aroma floral", "", 64,
        True),
    pro("QM_LIM_002", "Jabón de Tocador (3 unidades)", "Goods", "QM-LIM-002",
        "7401005300029", 15.0, 9.0, 0.3, "Jabón humectante paquete de 3", "", 110, True),
    pro("QM_LIM_003", "Papel Higiénico (12 rollos)", "Goods", "QM-LIM-003",
        "7401005300036", 45.0, 30.0, 1.4, "Papel higiénico doble hoja", "", 0, False),
]

PRODUCTOS_REGISTRO = [
    pro("QM_LAC_001", "Leche Entera 1 L", "Goods", "QM-LAC-001", "7401005400019", 13.5,
        9.25, 1.03, "Leche entera pasteurizada", "", 180, True),
    pro("QM_LAC_002", "Queso Fresco 1 lb", "Goods", "QM-LAC-002", "7401005400026", 30.0,
        21.0, 0.45, "Queso fresco artesanal", "", 40, True),
    pro("QM_SER_002", "Armado de Canasta Navideña", "Service", "QM-SER-002", "", 50.0,
        20.0, "", "Servicio de armado y empaque de canastas", "", 15, False),
    # barcode repetido de otro producto -> rechazado
    pro("QM_LAC_003", "Yogurt de Fresa 1 L", "Goods", "QM-LAC-003", "7401005400019",
        19.0, 12.0, 1.0, "", "", 25, True),
    # External ID repetido (ya viene en productos - bebidas.xlsx) -> rechazado
    pro("QM_BEB_001", "Agua Pura (duplicada)", "Goods", "QM-BEB-901", "", 5, 2.5, "",
        "", "", 10, True),
]

HOJA_PROVEEDOR = [["Proveedor", "NIT", "Contacto", "Teléfono"],
                  ["Distribuidora La Fragua", "123456-7", "Ing. Ramírez", "+502 2420 1100"],
                  ["Productos Lácteos Xelac", "998877-6", "Licda. Toc", "+502 7763 9000"],
                  ["Importadora del Pacífico", "556677-1", "Sr. López", "+502 7880 4321"]]
HOJA_RECLAMOS = [["No. Reclamo", "Fecha", "Cliente", "Motivo", "Estado"],
                 ["R-2026-001", "2026-09-02", "Tienda Doña Tere", "Producto vencido", "Abierto"],
                 ["R-2026-002", "2026-09-05", "Carlos Enrique Pérez", "Cobro doble", "Cerrado"],
                 ["R-2026-003", "2026-09-11", "Fernanda Ríos", "Entrega tardía", "Abierto"]]
HOJA_REGISTROS = [["Fecha", "Sucursal", "Movimiento", "Monto Q"],
                  ["2026-09-01", "Guatemala", "Venta", 15230.5],
                  ["2026-09-01", "México", "Venta", 8840.0],
                  ["2026-09-02", "El Salvador", "Compra", 4300.25]]
HOJA_NOTAS = [["Notas"], ["Revisar precios con gerencia"], ["No borrar esta hoja"]]


# ----------------------------------------------------------------------------- utilidades
def xlsx(path: Path, hojas: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for nombre, filas in hojas.items():
        ws = wb.create_sheet(nombre)
        for fila in filas:
            ws.append([None if v == "" else v for v in fila])
    wb.save(path)


def xls(path: Path, hojas: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = xlwt.Workbook(encoding="utf-8")
    for nombre, filas in hojas.items():
        ws = wb.add_sheet(nombre)
        for r, fila in enumerate(filas):
            for c, v in enumerate(fila):
                if v != "":
                    ws.write(r, c, v)
    wb.save(str(path))


def obtener_ruta_ejemplo(nombre: str) -> Path:
    """Busca el archivo de ejemplo en Docs/ArchivosPrueba o en Docs directamente."""
    for candidato in [DOCS / "ArchivosPrueba" / nombre, DOCS / nombre]:
        if candidato.exists():
            return candidato
    raise FileNotFoundError(f"No se encontró '{nombre}' en {DOCS} ni en {DOCS / 'ArchivosPrueba'}")


def main():
    if RAIZ.exists():
        shutil.rmtree(RAIZ)

    C = lambda filas: [COLS_CLI] + filas
    P = lambda filas: [COLS_PRO] + filas

    # clientes - ...
    xlsx(RAIZ / "clientes - cartera 2026" / "clientes - zona central.xlsx",
         {"resumen": HOJA_NOTAS, "clientes": C(CLIENTES_CENTRAL), "notas": HOJA_NOTAS})
    shutil.copy(obtener_ruta_ejemplo("clientes-archivo de ejemplo.xlsx"),
                RAIZ / "clientes - cartera 2026" / "clientes - archivo de ejemplo auxiliar.xlsx")
    xlsx(RAIZ / "clientes - cartera 2026" / "clientes - antiguos (revisar)" /
         "clientes - borrador sin hoja valida.xlsx",
         {"clientes_old": C(CLIENTES_CENTRAL[:2]), "notas": HOJA_NOTAS})

    # productos - ...
    (RAIZ / "productos - catalogo general").mkdir(parents=True, exist_ok=True)
    shutil.copy(obtener_ruta_ejemplo("productos - archivo de ejemplo.xls"),
                RAIZ / "productos - catalogo general" / "productos - archivo de ejemplo auxiliar.xls")
    xlsx(RAIZ / "productos - catalogo general" / "productos - abarrotes y bebidas" /
         "productos - bebidas.xlsx",
         {"PRODUCTOS": P(PRODUCTOS_BEBIDAS), "precios viejos": HOJA_REGISTROS})
    xlsx(RAIZ / "productos - catalogo general" / "productos - abarrotes y bebidas" /
         "productos - abarrotes (con errores).xlsx",
         {"productos ": P(PRODUCTOS_ABARROTES)})  # nombre con espacio al final

    # proveedores - ...
    xlsx(RAIZ / "proveedores - contactos" / "proveedores - lista 2026.xlsx",
         {"proveedor": HOJA_PROVEEDOR})
    xlsx(RAIZ / "proveedores - contactos" / "proveedores - pedidos" /
         "proveedores - mixto con productos.xlsx",
         {"proveedor": HOJA_PROVEEDOR, "productos": P(PRODUCTOS_PROVEEDOR)})

    # reclamos - ...
    xlsx(RAIZ / "reclamos - pendientes" / "reclamos - septiembre.xlsx",
         {"reclamos": HOJA_RECLAMOS})
    xlsx(RAIZ / "reclamos - pendientes" / "reclamos - sucursales mx y sv.xlsx",
         {"reclamos": HOJA_RECLAMOS, "Clientes": C(CLIENTES_RECLAMOS)})

    # registro - ...
    xls(RAIZ / "registro - movimientos" / "registro - general.xls",
        {"registros": HOJA_REGISTROS, "clientes": C(CLIENTES_REGISTRO),
         "productos": P(PRODUCTOS_REGISTRO)})
    xlsx(RAIZ / "registro - movimientos" / "2026" / "registro - solo movimientos.xlsx",
         {"registros": HOJA_REGISTROS, "notas": HOJA_NOTAS})
    (RAIZ / "registro - movimientos" / "leeme - notas varias.txt").write_text(
        "Archivo que no es Excel: el robot debe ignorarlo.\n", encoding="utf-8")

    archivos = sorted(p.relative_to(DESTINO) for p in RAIZ.rglob("*") if p.is_file())
    print(f"Estructura generada en: {RAIZ}")
    for a in archivos:
        print("  -", a)

    zip_repo = shutil.make_archive(str(BASE / "DatosPrueba"), "zip", DESTINO)
    print(f"Copia comprimida: {zip_repo}")


if __name__ == "__main__":
    main()
