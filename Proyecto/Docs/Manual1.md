# SECCIÓN 4: AUTOMATIZACIÓN DE PROCESOS ROBÓTICOS (RPA) CON UIPATH

---

## 4.1. PASO A PASO DE LA IMPLEMENTACIÓN DEL ROBOT (SOLUCIÓN A PROBLEMAS)

A continuación se detalla cada una de las fases desarrolladas dentro del flujo de trabajo de UiPath para dar solución a los problemas planteados (dispersión de carpetas, hojas heterogéneas, inconsistencias de datos y carga masiva web), acompañadas de las capturas correspondientes.

### PASO 1: Parametrización en Archivo Externo (`Config.xlsx`)
Para evitar valores codificados de forma rígida (*hardcoded*) y permitir una ejecución flexible tanto en entornos de pruebas locales como en los servidores de producción en la nube, se creó el libro `Config.xlsx`.

* **Parámetros configurados en Config.xlsx:**
  * `RutaEntrada`: `C:\QuetzalMart_RPA\Entrada` (árbol de carpetas y archivos desordenados).
  * `RutaSalida`: `C:\QuetzalMart_RPA\Salida` (directorio para los 5 archivos consolidados y el log de auditoría).
  * `OdooUrl`: `https://quetzalmart.store` (URL pública del ERP Odoo).
  * `OdooDb`: `quetzalmart` (Base de datos empresarial en PostgreSQL).
  * `OdooUser`: `<CORREO_ADMINISTRADOR>` (Usuario con privilegios de importación).
  * `OdooPassword`: `<PASSWORD_ADMINISTRADOR>` (Contraseña parametrizada en Config.xlsx).
  * `VersionOdoo`: `18` (Versión de Odoo Community).
  * `UbicacionInventario`: `WH/Stock` (Ubicación predeterminada de almacenamiento).
  * `EjecutarImportacionWeb`: `False` (Modo consolidación rápida para generar y auditar los 5 libros Excel; alternable a `True` para ejecutar la importación automática en navegador).

* **Parámetros de Comprobación en Base de Datos (SQL):**
  * Servidor / Host: Servidor de base de datos del proyecto (`quetzalmart`)
  * Motor: PostgreSQL
  * Base de datos: `quetzalmart`
  * Usuario: Cuenta de solo lectura / consulta

![Captura 4.1 - Archivo de Configuración Config.xlsx](Capturas/4.1.PNG)
> **Captura 4.1:** *Vista del archivo `Config.xlsx` en Excel mostrando la hoja `Settings` con las variables de configuración parametrizadas externamente sin quemar credenciales en el código fuente.*

---

### PASO 2: Inicialización de Esquemas de Datos (`InicializarTablas.xaml`)
En este workflow se inicializan en memoria las estructuras tabulares (`DataTable`) que albergarán la información consolidada durante el ciclo de vida del robot:

1. `dtCliEmp`: Clientes que son empresas o no tienen compañía padre asignada.
2. `dtCliPer`: Clientes que corresponden a personas/contactos vinculados a una empresa (`parent_id`). Se separan en dos archivos para garantizar la integridad referencial en Odoo (primero deben existir las empresas matrices antes de crear los contactos asociados).
3. `dtPro`: Catálogo consolidado de productos con sus atributos comerciales y técnicos.
4. `dtInv`: Registro de ajustes físicos de inventario para alimentar la *Cantidad a la mano*.
5. `dtLog`: Estructura de auditoría donde se registran los rechazos y advertencias fila por fila.

![Captura 4.2 - Inicialización de Esquemas de Datos](Capturas/4.2.jpg)
> **Captura 4.2:** *Diagrama del workflow `InicializarTablas.xaml` en UiPath Studio mostrando la secuencia modular que construye los esquemas de datos para clientes, productos, inventario y log.*

---

### PASO 3: Recorrido Recursivo e Identificación de Hojas (`ProcesarArchivos.xaml`)
Para cumplir el requerimiento de inspeccionar todas las carpetas sin importar la profundidad de los subdirectorios, el robot ejecuta:
1. `Directory.GetFiles(in_RutaEntrada, "*.*", SearchOption.AllDirectories)`: Recupera la totalidad de los archivos contenidos en el árbol.
2. Filtro de extensiones: Se verifica que el archivo finalice en `.xlsx`, `.xls` o `.xlsm` y que no sea un archivo temporal bloqueado (`~$...`).
3. Lectura de estructura con `Excel Application Scope` y `Get Workbook Sheets`: Se obtiene la lista dinámica de todas las hojas existentes en el libro.
4. Evaluación insensible a mayúsculas/minúsculas y espacios:
   * Si la hoja se llama `"clientes"`, se extrae con `Read Range` y se transfiere al módulo de validación de clientes.
   * Si la hoja se llama `"productos"`, se extrae con `Read Range` y se transfiere al módulo de validación de productos.
   * Cualquier otra hoja (`proveedor`, `reclamos`, `registros`, etc.) es omitida de forma automática.

![Captura 4.3 - Recorrido Recursivo e Identificación de Hojas](Capturas/4.3.jpg)
> **Captura 4.3:** *Workflow `ProcesarArchivos.xaml` en UiPath Studio mostrando el bucle `For Each` de archivos, el `Excel Application Scope` y las condiciones `If` evaluando los nombres de hoja.*

---

### PASO 4: Reglas de Negocio y Validación Rigurosa (`Invoke Code`)
Para asegurar un rendimiento óptimo al procesar miles de filas y mantener reglas de validación complejas sin sobrecargar el lienzo con decenas de actividades individuales, se implementaron rutinas en VB.NET encapsuladas en actividades `Invoke Code`.

#### A. Validación de Clientes (`ValidarClientes.vb`)
* **Mapeo Inteligente de Columnas:** Tolera encabezados con o sin asterisco, en inglés o español (`Name*`, `Nombre`, `Company Type*`, `Tipo de compañía`, etc.).
* **Campos Obligatorios:** `Name` y `Company Type` deben contener datos. Si faltan, la fila se rechaza inmediatamente.
* **Normalización de Tipos:** Se homologa `Company` o `Person` independientemente de si venía como *Empresa*, *Persona*, *Individual*.
* **Validación de Correo:** Expresión regular para garantizar que el email cumpla la estructura estándar `usuario@dominio.ext`.
* **Detección de Duplicados:** Se compara la tupla `(Nombre, Email)` contra los registros ya admitidos en memoria.
* **External ID Seguro:** Se genera un identificador único basado en la referencia o el nombre (`qm_cli_...`) para permitir idempotencia en Odoo.

#### B. Validación de Productos e Inventario (`ValidarProductos.vb`)
* **Campos Obligatorios:** `External ID` (id), `Name` y `Product Type`.
* **Tipos de Producto Odoo:** Se homologa a `Goods` (bienes almacenables) o `Service` (servicios). En Odoo 18 se incluye automáticamente la bandera técnica `is_storable = True`.
* **Validación Numérica:** `Sales Price`, `Cost`, `Weight` y `Cantidad a la mano` deben ser valores numéricos válidos mayores o iguales a cero. Si son negativos o contienen texto, la fila se rechaza.
* **Gestión del Estado Publicado:**
  * Si la columna `Está publicado` indica *True*, *Verdadero*, *Sí*, *1* o *Publicado*, se marca con `is_published = True`.
  * Si indica *False*, *No*, *0* o vacío, se marca con `is_published = False`.
  * Valores ambiguos generan rechazo de fila.
* **Regla de Negocio para Servicios:** Si un producto es de tipo `Service`, no puede almacenar unidades en bodega. Si el archivo contenía una cantidad a la mano, el robot registra una advertencia en el log y no crea línea de ajuste de inventario.
* **Separación de Inventario:** Para cada bien físico con existencias mayores a cero, se crea una línea vinculada a la ubicación de almacén (`WH/Stock`) lista para impactar la tabla de quants.

![Captura 4.4 - Reglas de Negocio en VB.NET](Capturas/4.4.PNG)
> **Captura 4.4:** *Propiedades y editor de código de la actividad `Invoke Code` en UiPath Studio con el código VB.NET y los argumentos `dtHoja`, `dtPro`, `dtInv` y `dtLog`.*

---

### PASO 5: Generación de Entregables Consolidados (`GuardarConsolidados.xaml`)
Una vez concluido el barrido de todas las carpetas, el robot invoca la actividad `Write Range` para plasmar los datos en la carpeta de salida:
1. `01_clientes_empresas.xlsx`: Empresas y clientes individuales independientes.
2. `02_clientes_contactos.xlsx`: Contactos vinculados a sus empresas matrices mediante la columna `parent_id`.
3. `03_productos.xlsx`: Catálogo maestro con precios, costos, pesos, referencias y visibilidad web (`is_published`).
4. `04_inventario_cantidad_a_la_mano.xlsx`: Archivo para el ajuste de inventario con `product_id`, `location_id` y `inventory_quantity`.
5. `log_filas_rechazadas.xlsx`: Registro de auditoría con las columnas `Tipo` (RECHAZADO/ADVERTENCIA), `Entidad`, `Archivo`, `Hoja`, `Fila`, `Identificador` y `Motivo`.

![Captura 4.5 - Archivos Consolidados Generados](Capturas/4.5.PNG)
> **Captura 4.5:** *Explorador de Windows mostrando los cinco archivos Excel generados en la carpeta `C:\QuetzalMart_RPA\Salida`.*

![Captura 4.6 - Log de Filas Rechazadas](Capturas/4.6.PNG)
> **Captura 4.6:** *Vista previa del archivo `log_filas_rechazadas.xlsx` mostrando el detalle exacto de las filas descartadas por Name vacío, correos inválidos, precios erróneos y duplicados.*

---

### PASO 6: Automatización de la Carga Web en Odoo (`ImportarOdooWeb.xaml`)
De acuerdo con las directrices del proyecto, la carga se realiza exclusivamente a través de la interfaz web de Odoo Community, emulando la interacción del navegador web (Microsoft Edge o Google Chrome, ambos basados en el motor Chromium) sin utilizar la API XML-RPC:

1. **Autenticación:** El robot abre el navegador (Microsoft Edge por defecto en Windows), navega a `/web/login`, ingresa el usuario y contraseña del administrador y presiona el botón de envío.
2. **Importación de Clientes Empresas:**
   * Navega a la vista de lista de contactos (`/odoo/contacts?view_type=list`).
   * Despliega el menú de acciones (icono de engranaje) y hace clic en `Import records`.
   * Pulsa `Upload Data File`, interactúa con el cuadro de diálogo del sistema operativo seleccionando `01_clientes_empresas.xlsx` y ejecuta `Import`.
3. **Importación de Contactos Relacionados:**
   * Repite el proceso con `02_clientes_contactos.xlsx`, resolviendo los vínculos hacia las empresas recién creadas.
4. **Importación del Catálogo de Productos:**
   * Navega a la lista de productos (`/odoo/inventory/products?view_type=list`).
   * Abre el asistente de importación, carga `03_productos.xlsx` y valida la importación masiva. Los productos quedan registrados con su precio de venta, costo y estado de publicación en la tienda online.
5. **Ajuste de Cantidad a la Mano (Inventario):**
   * Navega a la sección de inventario físico (`/odoo/action-419` o `/odoo/physical-inventory`).
   * Carga el archivo `04_inventario_cantidad_a_la_mano.xlsx`.
   * Presiona el botón `Apply All` (*Aplicar todo*) para actualizar el stock real en la ubicación interna `WH/Existencias`.

![Captura 4.7 - Secuencia de Automatización Web en Odoo](Capturas/4.7.jpg)
> **Captura 4.7:** *Secuencia de UI Automation en UiPath Studio mostrando las actividades `Open Browser`, `Type Into`, `Click` y selectores para la navegación web en Odoo.*

![Captura 4.8 - Asistente de Importación de Odoo](Capturas/4.8.jpeg)
> **Captura 4.8:** *Asistente de importación de Odoo Community en pantalla completa mostrando el archivo de productos cargado y el mapeo automático de campos.*

![Captura 4.9 - Catálogo de Productos y Existencias en Odoo](Capturas/4.9.jpeg)
> **Captura 4.9:** *Vista del catálogo de productos en Odoo tras la ejecución del RPA, demostrando los productos publicados y las cantidades a la mano actualizadas.*

---

## 4.2. VENTAJAS DE IMPLEMENTAR RPA EN QUETZALMART

La adopción de Robotic Process Automation en la cadena de tiendas QuetzalMart genera un impacto sustancial en múltiples dimensiones operativas, financieras y estratégicas:

### 1. Eliminación Radical del Tiempo de Operación Manual
* **Antes del RPA:** La revisión manual de decenas de carpetas y libros dispersos, la extracción de hojas y la digitación en Odoo tomaba un estimado de **20 a 30 horas hombre** por lote de sucursal.
* **Con el RPA:** El robot recorre el árbol completo, valida reglas complejas y prepara los consolidados en **menos de 30 segundos**, ejecutando la carga web en menos de 2 minutos. Esto representa una reducción de tiempo superior al **98%**.

### 2. Cero Tolerancia a Errores y Calidad de Datos Garantizada
* El factor humano al copiar y pegar datos suele introducir errores de digitación (comas por puntos en precios, correos mal escritos, omisión de campos requeridos).
* El robot aplica reglas determinísticas al 100%: no permite que ningún registro incompleto o corrupto ingrese a la base de datos empresarial de QuetzalMart.

### 3. Trazabilidad y Auditoría Total (Log de Rechazos)
* En un proceso manual, los datos erróneos se pierden o se ignoran sin registro.
* El robot genera un archivo formal (`log_filas_rechazadas.xlsx`) que identifica el archivo de origen, la hoja, el número de fila, el dato causante y el motivo exacto del rechazo. Esto permite al departamento de ventas corregir en el origen los datos problemáticos.

### 4. Respeto Estricto a la Arquitectura Sin Alterar APIs
* Al utilizar la interfaz gráfica web nativa de Odoo, el robot respeta todos los mecanismos de seguridad, permisos de usuario y reglas de negocio del framework web de Odoo sin requerir exponer puertos, programar controladores REST o habilitar servicios API externos que pudieran vulnerar la seguridad de la nube.

### 5. Escalabilidad Inmediata ante Nuevas Sucursales
* Ante la apertura planificada de nuevas tiendas en otros países de la región centroamericana, no se requiere contratar más personal operativo para procesar catálogos. La misma infraestructura de automatización puede procesar 10 o 1,000 archivos sin variaciones en el costo marginal.

### 6. Liberación de Talento Humano para Tareas Estratégicas
* Los colaboradores de ventas y TI dejan de actuar como "transcripteurs de datos" y pueden dedicar su tiempo a optimizar campañas de mercadeo, mejorar la atención al cliente y analizar las tendencias comerciales que impulsen la rentabilidad de QuetzalMart.


