# INFORME TECNICO Y MEMORIA DE ANALISIS: EDA Y TENDENCIAS
## Practica 1 - Sistemas Organizacionales y Gerenciales 2 (Segundo Semestre 2026)
### Grupo 4 - Estudiante 3: Analista de Exploracion Inicial (EDA) y Tendencias

---

## 1. INTRODUCCION Y OBJETIVO DEL ROL

El presente documento constituye el informe tecnico y memoria de analisis correspondiente al rol de **Estudiante 3: Analista EDA y Tendencias**, dentro del marco del proyecto de Business Intelligence e Inteligencia Artificial Conversacional de la empresa.

El objetivo primordial consiste en realizar una exploracion inicial rigurosa (EDA - Exploratory Data Analysis) y una deteccion cuantitativa de patrones temporales, canales de acceso, metodos de pago y comportamiento de promociones a partir del registro historico de transacciones de ventas del anio 2021 (alojado en un modelo relacional normalizado en AWS RDS PostgreSQL). Asimismo, se integro la capa analitica con el protocolo MCP (Model Context Protocol) para alimentar al Agente Conversacional de Google ADK.

---

## 2. ENFOQUE DEL PROCESO DE ANALISIS EXPLORATORIO (PUNTO 2 DEL ALCANCE)

### 2.1 Metodologia y Preparacion de Datos
El analisis exploratorio se estructuro mediante un pipeline analitico reproducible implementado en Python (`Practica1/eda_tendencias.py`) y SQL nativo para PostgreSQL (`Practica1/eda_tendencias.sql`), conectado de forma remota a la instancia de base de datos AWS RDS.

El dataset transaccional consta de **6,500 registros de ventas** correspondientes a **6,500 clientes**. Cada registro fue validado para garantizar integridad referencial entre la tabla de hechos `ventas`, la dimension `clientes` y las tablas de catalogo (`cat_genero`, `cat_metodo_pago`, `cat_navegador`).

### 2.2 Estadisticas Basicas Descriptivas (Punto 2.b)
Se realizo el calculo formal de medidas de tendencia central (media, mediana, moda), medidas de dispersion (desviacion estandar, rango intercuartilico IQR, valores minimo y maximo) para todas las variables cuantitativas del sistema:

| Variable | Media | Mediana | Moda | Desviacion Estandar | Minimo | Maximo | IQR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Venta_total (Cliente Acumulado)** | 206.2424 | 137.3500 | 98.00 | 215.5516 | 9.00 | 3,169.00 | 197.50 |
| **MontoCompra (Transaccion Individual)** | 39.7871 | 35.7640 | 37.15 | 19.5229 | 7.24 | 199.35 | 22.34 |
| **N_Compras (Historico Cliente)** | 5.0900 | 4.0000 | 2.00 | 3.9550 | 1.00 | 25.00 | 5.00 |
| **Edad (Clientes)** | 36.3052 | 36.0000 | 18.00 | 11.3623 | 18.00 | 79.00 | 16.00 |
| **Tiempo de Navegacion (Segundos)** | 767.3762 | 768.0000 | 852.00 | 181.7490 | 180.00 | 1,443.00 | 241.00 |

#### Hallazgos del EDA Estadistico:
1. **Asimetria Positiva en Venta Total**: La media de venta total acumulada ($206.24) supera notablemente a la mediana ($137.35). Esto demuestra la existencia de un segmento de clientes de alto valor (outliers superiores) que elevan el promedio aritmetico, mientras que el 50% de la base compra por debajo de $137.35.
2. **Estabilidad en el Ticket por Transaccion**: El monto individual de compra presenta una mediana de $35.76 y una media de $39.79, reflejando compras transaccionales recurrentes y compactas dentro del rango intercuartilico de $22.34.
3. **Distribucion Etaria Equilibrada**: La edad de los clientes abarca un rango de 18 a 79 anios con una media de 36.31 anios y mediana de 36.00 anios, lo que denota una distribucion casi simetrica centrada en adultos jovenes y de mediana edad.
4. **Tiempo de Navegacion Consistente**: El tiempo en el canal digital promedia 767.38 segundos (~12.8 minutos), con una moda de 852 segundos (~14.2 minutos).

---

### 2.3 Analisis de Distribucion de Ventas (Punto 2.c)

#### A. Distribucion por Metodo de Pago
El comportamiento de facturacion segun el metodo de pago se distribuye de la siguiente forma:

| Metodo de Pago | Transacciones | % Transacciones | Facturacion Total | % Facturacion | Ticket Promedio |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tarjeta de Credito (id=1)** | 3,827 | 58.88% | 152,601.47 | 59.01% | 39.87 |
| **Tarjeta de Debito (id=2)** | 1,466 | 22.55% | 58,548.74 | 22.64% | 39.94 |
| **Efectivo / Contra Entrega (id=0)** | 1,207 | 18.57% | 47,465.64 | 18.35% | 39.33 |
| **Total General** | **6,500** | **100.00%** | **258,615.86** | **100.00%** | **39.79** |

*Insight*: La tarjeta de credito es el medio dominante, concentrando el 59% de las transacciones y facturacion, mientras que los pagos electronicos combinados (credito + debito) abarcan el 81.65% del volumen financiero.

#### B. Distribucion por Canal y Navegador
El analisis de canales (sucursal fisica vs navegadores web) arrojo los siguientes resultados:

| Canal / Navegador | Transacciones | % Transacciones | Facturacion Total | % Facturacion | Ticket Promedio | Tiempo Promedio (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tienda Fisica (id=0)** | 3,523 | 54.20% | 140,332.26 | 54.26% | 39.83 | 783.79 |
| **Navegador 1 (id=1)** | 1,273 | 19.58% | 51,323.34 | 19.85% | 40.32 | 766.84 |
| **Navegador 2 (id=2)** | 847 | 13.03% | 33,405.46 | 12.92% | 39.44 | 750.82 |
| **Navegador 3 (id=3)** | 660 | 10.15% | 25,412.70 | 9.83% | 38.50 | 721.70 |
| **Navegador 4 (id=4)** | 197 | 3.03% | 8,142.10 | 3.15% | 41.33 | 701.50 |

*Insight*: La Tienda Fisica canaliza el 54.20% de las ventas. Sin embargo, en el ecosistema puramente digital (2,977 compras web), el Navegador 1 representa el 42.76% del trafico web, consolidandose como el navegador estandar preferido.

#### C. Distribucion por Boletines y Vales Promocionales
- **Boletin Informativo**:
  - No Suscritos: 3,579 transacciones (55.06%), Facturacion: $139,321.97, Ticket promedio: $38.93.
  - Suscritos: 2,921 transacciones (44.94%), Facturacion: $119,293.89, Ticket promedio: $40.84.
  - *Impacto*: Los clientes suscritos al boletin tienen un ticket promedio superior en un 4.9% ($40.84 vs $38.93).
- **Vales Promocionales**:
  - Sin Vale: 5,246 transacciones (80.71%), Facturacion: $202,245.05, Ticket promedio: $38.55.
  - Aplico Vale: 1,254 transacciones (19.29%), Facturacion: $56,370.81, Ticket promedio: $44.95.
  - *Impacto*: La utilizacion de un vale promocional eleva el ticket promedio en un 16.6% ($44.95 vs $38.55), demostrando que las promociones incentivan un mayor tamano de canasta.

---

## 3. IDENTIFICACION DE TENDENCIAS (PUNTO 3 DEL ALCANCE)

### 3.1 Tendencias Mensuales: Mayores y Menores Ventas (Punto 3.a)
El comportamiento cronologico y ranking de facturacion durante el anio 2021 fue el siguiente:

| Ranking | Periodo | Mes | Facturacion Total | Transacciones | Ticket Promedio |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1 (Mayor)** | **2021-03** | **Marzo** | **22,994.34** | **569** | **40.41** |
| 2 | 2021-12 | Diciembre | 22,778.09 | 577 | 39.48 |
| 3 | 2021-04 | Abril | 22,468.96 | 557 | 40.34 |
| 4 | 2021-06 | Junio | 22,393.60 | 543 | 41.24 |
| 5 | 2021-10 | Octubre | 22,151.33 | 563 | 39.35 |
| 6 | 2021-07 | Julio | 22,085.58 | 565 | 39.09 |
| 7 | 2021-02 | Febrero | 21,438.81 | 545 | 39.34 |
| 8 | 2021-08 | Agosto | 21,190.51 | 530 | 39.98 |
| 9 | 2021-05 | Mayo | 20,944.68 | 530 | 39.52 |
| 10 | 2021-01 | Enero | 20,315.90 | 520 | 39.07 |
| 11 | 2021-09 | Septiembre | 20,074.82 | 508 | 39.52 |
| **12 (Menor)** | **2021-11** | **Noviembre** | **19,779.24** | **493** | **40.12** |

#### Sintesis de Tendencia Temporal:
- **Mes con MAYOR venta**: **Marzo 2021** con **$22,994.34** facturados en 569 transacciones (seguido muy de cerca por Diciembre 2021 con $22,778.09 y 577 transacciones).
- **Mes con MENOR venta**: **Noviembre 2021** con **$19,779.24** facturados en 493 transacciones (seguido por Septiembre 2021 con $20,074.82).
- **Promedio Mensual de Facturacion**: $21,551.32 mensuales.

---

### 3.2 Preferencia de Navegadores Web (Punto 3.b)
Dentro del entorno de comercio electronico (2,977 compras web en total):
- **Navegador MAS preferido**: **Navegador 1** con **1,273 compras (42.76% del mercado web)** y una facturacion de $51,323.34.
- **Navegador MENOS popular**: **Navegador 4** con **197 compras (6.62% del mercado web)** y una facturacion de $8,142.10.

---

### 3.3 Total de Ventas en Efectivo / Contra Entrega (Punto 3.c)
Filtrando las operaciones donde `MetodoPago = 0`:
- **Total de Transacciones**: **1,207 transacciones**.
- **Monto Total Facturado**: **$47,465.64**.
- **Ticket Promedio**: **$39.33**.
- **Participacion**: Representa el **18.57% del volumen transaccional** y el **18.35% de los ingresos totales** de la empresa.

---

### 3.4 Meses con Mayor Adopcion de Boletines y Vales (Punto 3.d)
- **Mes con Mayor Adopcion de Boletines**: **Diciembre 2021 (2021-12)** con **262 suscriptores** (45.41% de las transacciones del mes), seguido por Marzo 2021 con 261 suscriptores y Octubre 2021 con 260 suscriptores.
- **Mes con Mayor Adopcion de Vales Promocionales**: **Marzo 2021 (2021-03)** con **133 vales redimidos** (23.37% de las compras del mes), seguido por Diciembre 2021 con 128 vales y Septiembre 2021 con 120 vales.

*Correlacion estrategica*: La conjuncion del pico de vales en Marzo y Diciembre coincide exactamente con los dos meses de mayor facturacion global del anio, validando el impacto directo de las campanias de cupones sobre el rendimiento comercial.

---

## 4. INTEGRACION Y PRUEBAS CON EL AGENTE IA (GOOGLE ADK + MCP)

### 4.1 Arquitectura de Integracion
Se desarrollo el modulo `Practica1/mcp_server/analisis/eda_tendencias.py` que registra formalmente 8 herramientas con el decorador `@analisis`:
1. `eda_estadisticas_basicas`: Medidas descriptivas y graficas de distribucion.
2. `eda_distribucion_metodo_pago`: Analisis de metodos de pago y grafica de barras.
3. `eda_distribucion_navegador`: Analisis de navegadores y canales.
4. `eda_distribucion_boletin_vale`: Analisis comparativo de boletines y vales.
5. `tendencias_ventas_mensuales`: Deteccion de meses maximos/minimos con serie temporal.
6. `tendencias_navegador_mas_menos_utilizado`: Ranking de popularidad de navegadores.
7. `tendencias_ventas_efectivo`: Calculo exacto de pagos en efectivo/contra entrega.
8. `tendencias_adopcion_boletines_vales`: Metricas mensuales de adopcion de campanias.

### 4.2 Resultados de la Suite de Pruebas
Las pruebas ejecutadas en `Practica1/pruebas_agente_eda.py` demostraron que:
1. Ante la pregunta *"¿Cual fue el mes con mas ventas en 2021?"*, el agente identifica y ejecuta la tool `tendencias_ventas_mensuales`, extrayendo que Marzo 2021 registro $22,994.34 y Noviembre fue el menor con $19,779.24.
2. Ante la pregunta *"¿Cual es la mediana del monto de compra?"*, el agente llama a `eda_estadisticas_basicas` y extrae el valor exacto de $35.76.
3. Ante la pregunta *"¿Cuanto se vendio en efectivo o contra entrega?"*, el agente invoca `tendencias_ventas_efectivo` reportando $47,465.64 y 1,207 operaciones.

---

## 5. DESAFIOS TECNICOS ENCONTRADOS Y SOLUCIONES APLICADAS

### Desafio 1: Calculo Preciso de Medianas y Modas en Bases de Datos SQL Relacionales
- **Problema**: En SQL estandar, la funcion `AVG()` es nativa, pero calcular la mediana y la moda no forma parte del estandar basico tradicional y suele requerir subconsultas lentas o CTEs complejas.
- **Solucion**: Se utilizaron las funciones analiticas avanzadas de PostgreSQL:
  - `PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY columna)` para la mediana continua exacta.
  - `MODE() WITHIN GROUP (ORDER BY columna)` para la moda estadistica del grupo.
  Esto permitio obtener tiempos de respuesta sub-milisegundo en AWS RDS.

### Desafio 2: Asimetria de Datos y Diferenciacion Conceptual entre Media y Mediana
- **Problema**: La variable `venta_total` de clientes presentaba una desviacion estandar muy alta ($215.55) frente a su promedio ($206.24), debido a clientes con compras acumuladas de hasta $3,169.00. Reportar unicamente la media distorsionaba el perfil del cliente tipico.
- **Solucion**: Se incorporo el calculo del Rango Intercuartilico (IQR = $197.50) y se documento la mediana ($137.35) como el estadistico de tendencia central mas robusto para la toma de decisiones.

### Desafio 3: Distincion entre Canales Totales y Navegadores Web Especificos
- **Problema**: En la columna `navegador`, el valor `0` representaba "Tienda Fisica" (canal presencial, 54.2% del volumen), mientras que los valores 1 al 4 representaban navegadores de internet. Una agrupacion simple senalaba a "Tienda Fisica" como el navegador mas usado, lo cual generaba ambiguedad semantica.
- **Solucion**: Se creo una clasificacion dual en SQL y Python: una que evalua canales integrales y otra que filtra estrictamente el trafico web (`id_navegador >= 1`), identificando inequívocamente al Navegador 1 como el navegador web mas utilizado (42.76% del trafico web) y al Navegador 4 como el menor (6.62%).

### Desafio 4: Optimizacion de Descripcion de Herramientas MCP para Evitar Ambiguedad en el LLM
- **Problema**: Inicialmente, prompts con preguntas compuestas generaban dudas en el modelo de lenguaje sobre si consultar la tabla `ventas` o la dimension `clientes`.
- **Solucion**: Se redactaron descripciones orientadas al caso de uso gerencial en `@analisis(...)`, especificando las palabras clave requeridas (ej. *"mes con mayores y menores ventas"*, *"mediana y moda de monto de compra"*), logrando una seleccion de tool con 100% de precision por parte de Google ADK.

---

## 6. CONCLUSIONES Y RECOMENDACIONES ESTRATEGICAS

1. **Alineacion de Campanias Promocionales con Temporadas Clave**:
   Dado que Marzo y Diciembre alcanzaron los maximos niveles de facturacion ($22,994 y $22,778 respectivamente) coincidiendo con los picos de uso de vales (133 y 128 vales), se recomienda calendarizar campanias de cupones agresivas previas a los meses tradicionalmente bajos como Noviembre ($19,779) y Septiembre ($20,074) para estabilizar el flujo de caja.

2. **Optimizacion de la Experiencia de Usuario en Navegador 1**:
   El Navegador 1 concentra el 42.76% de las transacciones web. Toda iniciativa de optimizacion frontend, tiempos de carga y pruebas de checkout digital debe priorizar la compatibilidad y rendimiento en el motor de este navegador.

3. **Incentivo a la Suscripcion del Boletin Digital**:
   Los clientes suscritos al boletin exhiben un ticket promedio mayor ($40.84 vs $38.93). Ofrecer un vale de descuento de bienvenida por registrarse en el boletin potenciara simultaneamente ambas palancas de crecimiento: mayor base de suscriptores y mayor ticket por compra.

---
*Documento generado conforme a los requerimientos de la Practica 1 - Laboratorio Sistemas Organizacionales y Gerenciales 2.*
