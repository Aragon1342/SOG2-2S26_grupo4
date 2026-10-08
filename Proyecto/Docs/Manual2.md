## 1. DIAGRAMA GENERAL DE CICLO DE VIDA (PIPELINE PRINCIPAL)

El siguiente diagrama modela el flujo orquestador principal (`Main.xaml`), el cual coordina secuencialmente la carga de parámetros externos, inicialización de estructuras en memoria, procesamiento de carpetas, generación de archivos consolidados y la interacción web con Odoo Community.

![Diagrama 1 - Pipeline Principal](Diagramas/Diagrama1.png)
> **Diagrama 1:** *Diagrama de flujo del pipeline principal (`Main.xaml`), mostrando la orquestación secuencial desde la lectura de configuración externa hasta la finalización del robot.*

---

## 2. DIAGRAMA DE FLUJO: ESCANEO RECURSIVO Y SELECCIÓN DE HOJAS

Modela el algoritmo implementado en `ProcesarArchivos.xaml` para recorrer recursivamente cualquier nivel de subcarpetas en la ruta de entrada, filtrando exclusivamente libros de Excel e inspeccionando el nombre de sus hojas.

![Diagrama 2 - Escaneo Recursivo y Selección de Hojas](Diagramas/Diagrama2.png)
> **Diagrama 2:** *Diagrama de flujo de `ProcesarArchivos.xaml`, ilustrando el recorrido recursivo de archivos, el filtro de extensiones válidas y la discriminación de hojas `clientes` y `productos`.*

---

## 3. DIAGRAMA DE FLUJO: VALIDACIÓN Y CONSOLIDACIÓN DE CLIENTES

Modela la lógica implementada en `ValidarClientes.vb`, encargada de validar campos obligatorios, verificar formatos de correo, detectar registros duplicados y clasificar entre empresas matrices y contactos relacionados.

![Diagrama 3 - Validación y Consolidación de Clientes](Diagramas/Diagrama3.png)
> **Diagrama 3:** *Diagrama de flujo de `ValidarClientes.vb`, detallando la cascada de validación de negocio, registro de rechazos en `dtLog` y separación entre `01_clientes_empresas.xlsx` y `02_clientes_contactos.xlsx`.*

---

## 4. DIAGRAMA DE FLUJO: VALIDACIÓN DE PRODUCTOS, VISIBILIDAD E INVENTARIO

Modela la lógica implementada en `ValidarProductos.vb` para comprobar campos mandatorios, validar precios y cantidades no negativas, clasificar entre bienes y servicios, gestionar la visibilidad en tienda web y generar las líneas de ajuste de inventario.

![Diagrama 4 - Validación de Productos, Visibilidad e Inventario](Diagramas/Diagrama4.png)
> **Diagrama 4:** *Diagrama de flujo de `ValidarProductos.vb`, mostrando las validaciones de campos clave, precios, reglas de servicios sin inventario y generación del catálogo de productos y ajustes de stock.*

---

## 5. DIAGRAMA DE FLUJO: AUTOMATIZACIÓN DE CARGA WEB EN ODOO

Modela la interacción visual a través de Microsoft Edge desarrollada en `ImportarOdooWeb.xaml` para emular el comportamiento del operador humano en el portal de Odoo Community.

![Diagrama 5 - Automatización de Carga Web en Odoo](Diagramas/Diagrama5.png)
> **Diagrama 5:** *Diagrama de flujo de `ImportarOdooWeb.xaml`, ilustrando la secuencia de navegación en Microsoft Edge sobre Odoo Community: autenticación, importación secuencial de los 4 archivos y aplicación masiva del inventario físico.*
