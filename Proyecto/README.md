# PROYECTO - SISTEMAS ORGANIZACIONALES Y GERENCIALES 2
## RPA CON UIPATH

## ESTRUCTURA DE LA CARPETA PROYECTO

```text
Proyecto/
├── Docs/                                          # Documentos base del proyecto y muestras
│   ├── Proyecto Segundo Semestre 2026.pdf         # Enunciado oficial del proyecto
│   ├── clientes-archivo de ejemplo.xlsx           # Archivo de ejemplo de clientes del auxiliar
│   └── productos - archivo de ejemplo.xls         # Archivo de ejemplo de productos del auxiliar
│
├── Manuales/                                      # Manuales y documentación requerida
│   ├── Manual1_Seccion4_RPA.md                    # Manual 1: Sección 4 (RPA paso a paso y ventajas)
│   └── Manual2_DiagramaFlujo_RPA.md               # Manual 2: Diagramas de flujo detallados del RPA
│
└── RPA/                                           # Componentes de automatización
    ├── DatosPrueba.zip                            # Copia comprimida del árbol desordenado de pruebas
    │
    ├── QuetzalMart_RPA/                           # Proyecto completo de UiPath Studio
    │   ├── project.json                           # Configuración del proyecto UiPath (Windows, VB)
    │   ├── Config.xlsx                            # Parámetros externos (Rutas, URLs, OdooDb, etc.)
    │   ├── Main.xaml                              # Workflow orquestador principal
    │   ├── CodigoVB/                              # Lógica VB.NET de validación
    │   │   ├── ValidarClientes.vb
    │   │   └── ValidarProductos.vb
    │   └── Workflows/                             # Flujos modulares del robot
    │       ├── InicializarTablas.xaml
    │       ├── ProcesarArchivos.xaml
    │       ├── GuardarConsolidados.xaml
    │       └── ImportarOdooWeb.xaml
    │
    ├── consultas_sql/                             # Consultas SQL para comprobación
    │   └── comprobacion_carga.sql                 # Consultas SELECT para validar la carga en Odoo DB
    │
    └── scripts/                                   # Scripts de datos de prueba
        └── generar_datos_prueba.py                # Generador del árbol desordenado con casos de prueba
```

---

## GUÍA DE EJECUCIÓN RÁPIDA

### 1. Generar la estructura de carpetas de prueba
Para generar el árbol de carpetas con nombres desordenados (`clientes - ...`, `productos - ...`, `proveedores - ...`, `reclamos - ...`, `registro - ...`) conteniendo los archivos de ejemplo del auxiliar y casos con errores para el log:
```powershell
python Proyecto/RPA/scripts/generar_datos_prueba.py
```
*Por defecto crea la estructura en `C:\QuetzalMart_RPA\Entrada` y actualiza `Proyecto/RPA/DatosPrueba.zip`.*

### 2. Abrir y ejecutar el Robot en UiPath Studio
1. Abre **UiPath Studio**.
2. Selecciona **Open Local Project** y navega a:
   `Proyecto\RPA\QuetzalMart_RPA\project.json`
3. Verifica que en `Config.xlsx` las credenciales y URL de Odoo correspondan a tu entorno.
4. Presiona **Run** (`F5`) en `Main.xaml`.
5. El robot generará en la carpeta de salida (`C:\QuetzalMart_RPA\Salida`):
   - `01_clientes_empresas.xlsx`
   - `02_clientes_contactos.xlsx`
   - `03_productos.xlsx`
   - `04_inventario_cantidad_a_la_mano.xlsx`
   - `log_filas_rechazadas.xlsx`
6. Si `EjecutarImportacionWeb = True`, abrirá Microsoft Edge y cargará los archivos en Odoo.

### 3. Comprobar la Carga en la Base de Datos
Conéctate a la base de datos de Odoo (PostgreSQL) y ejecuta las consultas contenidas en:
`Proyecto/RPA/consultas_sql/comprobacion_carga.sql`
Verificarás:
- Total de clientes cargados clasificados por External ID (`qm_%`, `cust%`).
- Jerarquía de empresas y sus contactos asociados (`parent_id`).
- Productos importados con precios, códigos de barra y estado publicado web.
- Existencias físicas consolidadas en bodega (`stock_quant` en `WH/Existencias`).
