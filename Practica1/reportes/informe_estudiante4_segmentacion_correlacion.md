# INFORME TÉCNICO DE SEGMENTACIÓN DE CLIENTES Y ANÁLISIS DE CORRELACIONES

**Práctica 1 — Sistemas Organizacionales y Gerenciales 2 (Segundo Semestre 2026)**  
**Estudiante 4:** Analista de Segmentación y Correlaciones (Puntos 4, 5 y 6 del Alcance)  
**Grupo:** 4 | **Base de Datos:** PostgreSQL en AWS RDS  

---

## 1. RESUMEN EJECUTIVO Y OBJETIVOS

El presente informe constituye la entrega técnica y gerencial del **Estudiante 4 (Analista de Segmentación y Correlaciones)** para la empresa de comercio electrónico en proceso de expansión física y adopción de IA conversacional.

El alcance encomendado comprende:
1. **Segmentación de Clientes (Punto 4):**
   - Agrupación por cohortes etarias (18-25, 26-40, 41-55, 56+) y análisis de hábitos de consumo.
   - Comparativa de comportamiento transaccional según género ($Genero = 0$ Masculino vs $Genero = 1$ Femenino).
   - Evaluación del impacto cruzado de herramientas de fidelización y promociones (Boletín informativo y Vales de descuento).
2. **Análisis de Correlación e Inferencia Estadística (Punto 5):**
   - Correlación paramétrica (Pearson) y no paramétrica (Spearman), junto con regresión por mínimos cuadrados ordinarios (OLS) entre Edad y Ventas.
   - Prueba de independencia Chi-cuadrado ($\chi^2$), grados de libertad y coeficiente $V$ de Cramér para Género vs. Método de Pago preferido.
   - Medición de la asociación de variables binarias entre Suscripción al Boletín y Redención de Vales (Coeficiente $\Phi$, prueba de Yates y Odds Ratio).
   - Matriz de correlación multivariable sobre todas las dimensiones analíticas.
3. **Generación y Justificación Metodológica de 7 Visualizaciones (Punto 6):**
   - Justificación teórica de cada tipo de gráfica acorde a la tipología de datos.
   - Interpretación técnica y gerencial de cada hallazgo con sus respectivas figuras de alta resolución.

---

## 2. METODOLOGÍA DE SELECCIÓN DE VISUALIZACIONES (Punto 6 del Alcance)

La selección del tipo de gráfico para cada hallazgo no fue arbitraria, sino fundamentada en la teoría de visualización de datos y la naturaleza de las variables:

| Gráfico N° | Nombre del Gráfico | Variables Representadas | Tipo de Variables | Justificación Metodológica |
| :--- | :--- | :--- | :--- | :--- |
| **Gráfico 1** | **Barras Agrupadas con Eje Gemelo** | Rango de Edad vs. Facturación Total y Ticket Promedio | Categórica Ordinal + Numérica Continua + Ratio | Permite contrastar simultáneamente el volumen macroeconómico total por cohorte (barras) con la intensidad individual de gasto (línea de ticket promedio) sin distorsionar escalas. |
| **Gráfico 2** | **Barras Comparativas Multimétrica** | Género (0 vs 1) vs. Facturación, Ticket y LTV | Categórica Nominal Binaria + Numéricas Continuas | Ideal para comparar magnitudes directas entre dos poblaciones independientes y verificar simetrías de mercado. |
| **Gráfico 3** | **Barras Horizontales Compuestas / Cuadrantes** | 4 Cuadrantes de Promoción vs. Facturación y Ticket | Categórica Nominal Combinada + Numérica Continua | La disposición horizontal facilita la lectura de etiquetas descriptivas extensas y el ordenamiento visual de desempeño comercial por clúster. |
| **Gráfico 4** | **Gráfico de Dispersión (Scatter Plot) con OLS** | Edad del Cliente vs. Venta Total Acumulada | Numérica Continua vs. Numérica Continua | Es el estándar estadístico para evaluar correlación, homocedasticidad, presencia de outliers y pendiente de la recta de regresión lineal. |
| **Gráfico 5** | **Mapa de Calor (Heatmap) de Contingencia** | Género vs. Método de Pago Preferido | Categórica Nominal (2) $\times$ Categórica Nominal (3) | Facilita la identificación visual instantánea de concentraciones de frecuencia porcentual y patrones de preferencia cruzada. |
| **Gráfico 6** | **Mapa de Calor de Correlación Multivariable** | 10 Variables del Modelo de Datos | Continuas, Discretas y Dummies Binarias | Muestra la matriz de coeficientes de Pearson ($r \in [-1, 1]$) con paleta divergente centrada en cero, permitiendo descubrir multicolinealidad. |
| **Gráfico 7** | **Diagrama de Caja y Bigotes (Boxplot) con Medias** | Segmento Promocional vs. Monto de Compra | Categórica Nominal (4 grupos) vs. Numérica Continua | Permite evaluar la mediana, cuartiles (Q1, Q3), rango intercuartílico (IQR), dispersión, asimetría y valores atípicos entre tratamientos. |

---

## 3. RESULTADOS DE LA SEGMENTACIÓN DE CLIENTES (Punto 4)

### 3.1. Segmentación por Rangos de Edad (Punto 4.a)

Se crearon 4 cohortes demográficas representativas del ciclo de vida del consumidor:
- **18-25 años (Jóvenes / Gen Z):** Etapa de inserción laboral o universitaria.
- **26-40 años (Adultos Jóvenes / Millennials):** Mayor poder adquisitivo y nativos del e-commerce.
- **41-55 años (Adultos / Gen X):** Consumo familiar consolidado.
- **56+ años (Adultos Mayores / Boomers):** Compradores selectivos de menor volumen digital.

#### Tabla 1: Desempeño Comercial por Cohorte Etaria
| Rango de Edad | Clientes Únicos | % Clientes | Transacciones | Facturación Total ($ USD) | % Facturación | Ticket Promedio ($) | Tiempo Sesión (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **18-25 (Gen Z)** | 1,061 | 16.32% | 1,061 | $41,414.73 | 16.01% | $39.03 | 763.51 s |
| **26-40 (Millennials)** | 3,425 | 52.69% | 3,425 | $136,547.45 | 52.80% | $39.87 | 770.83 s |
| **41-55 (Gen X)** | 1,607 | 24.72% | 1,607 | $64,300.91 | 24.86% | $40.01 | 765.17 s |
| **56+ (Boomers)** | 407 | 6.26% | 407 | $16,352.77 | 6.32% | $40.18 | 758.33 s |
| **TOTAL GENERAL** | **6,500** | **100.00%** | **6,500** | **$258,615.86** | **100.00%** | **$39.79** | **767.38 s** |

- **Análisis Estadístico:** Al aplicar la prueba **ANOVA de un factor** entre las 4 cohortes etarias para el monto de compra, se obtuvo un estadístico $F = 0.9419$ y un valor $p = 0.4193$. Dado que $p > 0.05$, se concluye que no existe diferencia estadísticamente significativa en el ticket promedio entre edades.
- **Hallazgo Gerencial:** Aunque el ticket unitario es uniforme (~$40), el **52.8% de los ingresos** proviene del segmento **26-40 años**, concentrando la base crítica del negocio.

---

### 3.2. Comparativa por Género ($0 = Masculino$ vs $1 = Femenino$) (Punto 4.b)

#### Tabla 2: Comparativa de Indicadores Clave por Género
| Género | Código | Clientes | % Clientes | Facturación Total ($) | % Facturación | Ticket Promedio ($) | Desv. Estándar ($) | LTV Promedio ($) | Tiempo Sesión (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Masculino** | 0 | 3,372 | 51.88% | $133,861.26 | 51.76% | $39.70 | $19.18 | $204.46 | 765.89 s |
| **Femenino** | 1 | 3,128 | 48.12% | $124,754.61 | 48.24% | $39.88 | $19.89 | $208.16 | 768.98 s |

- **Pruebas de Hipótesis de Medias:**
  - **Prueba t de Student para muestras independientes (Welch):** $t = -0.3818$, $p = 0.7026$.
  - **Prueba no paramétrica U de Mann-Whitney:** $U = 5,271,528.0$, $p = 0.9759$.
- **Interpretación:** Ambas distribuciones son estadísticamente indistinguibles ($p > 0.05$). La cartera de clientes presenta un equilibrio cercano al 52/48 con igual propensión de gasto, lo que indica que las ofertas y el catálogo son neutros y atractivos para ambos sexos.

---

### 3.3. Segmentación en Cuadrantes de Promoción y Fidelización (Punto 4.c)

Se cruzaron las dos herramientas comerciales: Boletín Informativo ($Boletin \in \{0, 1\}$) y Vales de Descuento ($Vale \in \{0, 1\}$).

#### Tabla 3: Matriz de Desempeño de los 4 Cuadrantes Promocionales
| Cuadrante de Fidelización | Transacciones | % Transaccional | Facturación Total ($) | % Facturación | Ticket Promedio ($) | Mediana ($) | Desv. Est. ($) | Tiempo Sesión (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Ambos (Boletín y Vale)** | 811 | 12.48% | $37,047.64 | 14.33% | **$45.68** | $41.48 | $21.76 | 777.21 s |
| **2. Solo Vale** | 443 | 6.82% | $19,323.17 | 7.47% | **$43.62** | $39.76 | $21.69 | 782.32 s |
| **3. Solo Boletín** | 2,110 | 32.46% | $82,246.25 | 31.80% | $38.98 | $35.10 | $18.81 | 766.40 s |
| **4. Ninguno (Orgánico)** | 3,136 | 48.25% | $119,998.80 | 46.40% | $38.26 | $34.58 | $18.70 | 763.38 s |

- **Prueba ANOVA Multigrupo:** $F = 38.5465$, $p = 1.1054 \times 10^{-24}$ (Altamente Significativo).
- **Hallazgo Clave:** Los clientes que aplican vales incrementan su ticket promedio en un **+19.4%** cuando están suscritos al boletín ($45.68 vs $38.26 del cliente orgánico), y un **+14.0%** sin boletín ($43.62 vs $38.26). El vale actúa como un potente acelerador del tamaño de la cesta de compra.

---

## 4. ANÁLISIS DE CORRELACIÓN E INFERENCIA ESTADÍSTICA (Punto 5)

### 4.1. Correlación entre Edad del Cliente y Ventas (Punto 5.a)

Se evaluó la relación entre la variable continua `edad` y dos métricas de ingresos: `venta_total` (acumulada del cliente) y `monto_compra` (transaccional).

#### Tabla 4: Parámetros de Correlación y Regresión OLS
| Relación Evaluada | Pearson ($r$) | Valor $p$ (Pearson) | Spearman ($\rho$) | Valor $p$ (Spearman) | Ecuación OLS | $R^2$ (Varianza Exp.) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Edad vs. Venta Total Acumulada** | -0.0252 | 0.0419 | -0.0298 | 0.0162 | $\text{Venta} = -0.4787 \cdot \text{Edad} + 223.62$ | 0.000637 (0.06%) |
| **Edad vs. Monto de Compra Trans.** | +0.0236 | 0.0572 | +0.0375 | 0.0025 | $\text{Monto} = +0.0405 \cdot \text{Edad} + 38.32$ | 0.000556 (0.05%) |

- **Interpretación Técnica:** Aunque la muestra grande ($N=6,500$) arroja valores $p$ marginales menores a 0.05, el coeficiente de correlación $r \approx -0.025$ y el $R^2 = 0.0006$ demuestran que **la edad no explica ni el 0.1% de la variabilidad del gasto**. La relación es prácticamente nula u ortogonal.

---

### 4.2. Correlación: Género vs. Método de Pago Preferido (Punto 5.b)

#### Tabla 5: Tabla de Contingencia Cruzada (Frecuencias Observadas y %)
| Género | Efectivo (0) | Tarjeta de Crédito (1) | Tarjeta de Débito (2) | Total |
| :--- | :---: | :---: | :---: | :---: |
| **Femenino (1)** | 606 (19.37%) | 1,806 (57.74%) | 716 (22.89%) | 3,128 (100.0%) |
| **Masculino (0)** | 601 (17.82%) | 2,021 (59.93%) | 750 (22.24%) | 3,372 (100.0%) |
| **TOTAL** | **1,207 (18.57%)** | **3,827 (58.88%)** | **1,466 (22.55%)** | **6,500 (100.0%)** |

- **Resultados de la Prueba Chi-Cuadrado de Independencia:**
  - Estadístico $\chi^2 = 3.7338$
  - Grados de Libertad ($dof$) $= 2$
  - Valor $p = 0.1546$ (No significativo al $\alpha = 0.05$)
  - Coeficiente $V$ de Cramér $= 0.02397$ (Asociación nula)
- **Conclusión:** Se acepta la hipótesis nula de independencia ($H_0$). El género del cliente no condiciona el método de pago seleccionado. Ambos grupos muestran una fuerte preferencia por la tarjeta de crédito (~58-60%).

---

### 4.3. Correlación entre Suscripción a Boletines y Uso de Vales (Punto 5.c)

#### Tabla 6: Matriz de Contingencia 2x2 (Boletín vs. Vale)
| Estado del Boletín | Sin Vale ($Vale=0$) | Con Vale ($Vale=1$) | Total | Tasa de Conversión a Vale (%) |
| :--- | :---: | :---: | :---: | :---: |
| **No Suscrito ($Boletin=0$)** | 3,136 | 443 | 3,579 | **12.38%** |
| **Suscrito ($Boletin=1$)** | 2,110 | 811 | 2,921 | **27.76%** |
| **TOTAL** | **5,246** | **1,254** | **6,500** | **19.29%** |

- **Estadísticas de Asociación:**
  - Coeficiente de Correlación $\Phi$ (Phi / Pearson para binarias): $\Phi = +0.19397$ ($p = 3.9275 \times 10^{-56}$).
  - Prueba Chi-cuadrado con corrección de Yates: $\chi^2 = 243.5653$ ($p = 6.5666 \times 10^{-55}$).
  - **Odds Ratio (Razón de Momios):**
    $$\text{Odds Ratio} = \frac{811 \times 3,136}{2,110 \times 443} = 2.7209$$
- **Interpretación Gerencial:** Un cliente suscrito al boletín informativo tiene **2.72 veces más probabilidades de redimir un vale promocional** que un cliente no suscrito. El boletín actúa como un canal de distribución altamente efectivo para dinamizar ofertas.

---

### 4.4. Matriz de Correlación Multivariable Global (Punto 5.d)

#### Tabla 7: Matriz de Correlación de Pearson ($r$) entre Variables Clave
| Variable | Edad | Género | Venta Total | N_Compras | Monto Compra | Tiempo | Boletín | Vale | Método Pago | Navegador |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Edad** | 1.000 | -0.010 | -0.025 | -0.050 | +0.024 | -0.010 | -0.016 | +0.006 | +0.027 | -0.001 |
| **Género** | -0.010 | 1.000 | +0.009 | -0.001 | +0.005 | +0.009 | +0.008 | +0.008 | -0.007 | +0.006 |
| **Venta Total** | -0.025 | +0.009 | 1.000 | +0.781 | +0.013 | +0.005 | +0.012 | +0.019 | +0.013 | -0.006 |
| **N_Compras** | -0.050 | -0.001 | +0.781 | 1.000 | +0.002 | +0.008 | +0.007 | +0.014 | +0.007 | +0.001 |
| **Monto Compra** | +0.024 | +0.005 | +0.013 | +0.002 | 1.000 | +0.011 | +0.021 | **+0.129** | +0.010 | -0.008 |
| **Tiempo** | -0.010 | +0.009 | +0.005 | +0.008 | +0.011 | 1.000 | +0.004 | +0.019 | -0.021 | **-0.125** |
| **Boletín** | -0.016 | +0.008 | +0.012 | +0.007 | +0.021 | +0.004 | 1.000 | **+0.194** | +0.003 | -0.027 |
| **Vale** | +0.006 | +0.008 | +0.019 | +0.014 | **+0.129** | +0.019 | **+0.194** | 1.000 | +0.035 | -0.014 |
| **Método Pago** | +0.027 | -0.007 | +0.013 | +0.007 | +0.010 | -0.021 | +0.003 | +0.035 | 1.000 | -0.087 |
| **Navegador** | -0.001 | +0.006 | -0.006 | +0.001 | -0.008 | **-0.125** | -0.027 | -0.014 | -0.087 | 1.000 |

---

## 5. CAPTURAS Y ANÁLISIS DE LAS 7 VISUALIZACIONES (Punto 6)

### Gráfica 1: Facturación Total y Ticket Promedio por Rango de Edad
![Gráfica 1](file:///c:/Users/chris/OneDrive/Escritorio/U/2S2026/Geren2/Lab/SOG2-2S26_grupo4/Practica1/graficas_segmentacion/01_segmentacion_edad_ventas_ticket.png)

- **Interpretación Técnica:** Las barras azules reflejan la masa monetaria recaudada en miles de dólares ($k), mientras que la línea roja traza el ticket medio. La cohorte de 26-40 años concentra el 52.8% de la facturación global ($136.5k). A pesar del gran volumen, la línea de ticket medio se mantiene notablemente plana entre $39.03 y $40.18, demostrando que la propensión de consumo individual no está sesgada por la edad.

---

### Gráfica 2: Comportamiento Comercial Comparativo según Género (0 vs 1)
![Gráfica 2](file:///c:/Users/chris/OneDrive/Escritorio/U/2S2026/Geren2/Lab/SOG2-2S26_grupo4/Practica1/graficas_segmentacion/02_segmentacion_genero_comportamiento.png)

- **Interpretación Técnica:** El panel izquierdo muestra la facturación total dividida entre Hombres ($133.9k, 51.8%) y Mujeres ($124.8k, 48.2%). El panel derecho contrasta el ticket medio ($39.70 vs $39.88) y el valor de vida del cliente acumulado ($204.46 vs $208.16). Las pruebas estadísticas confirman que no existe brecha de género en el valor comercial.

---

### Gráfica 3: Desempeño Comercial según Segmento de Fidelización (Boletín y Vales)
![Gráfica 3](file:///c:/Users/chris/OneDrive/Escritorio/U/2S2026/Geren2/Lab/SOG2-2S26_grupo4/Practica1/graficas_segmentacion/03_segmentacion_boletin_vales_cuadrantes.png)

- **Interpretación Técnica:** El segmento orgánico (sin promociones) genera la mayor masa de ventas brutas ($120.0k) pero tiene el ticket más bajo ($38.26). En contraste, los clientes combinados (Boletín + Vale) alcanzan un ticket superior de $45.68 (+19.4%), confirmando que las campañas promocionales incrementan el tamaño del carrito de compra.

---

### Gráfica 4: Análisis de Correlación y Dispersión: Edad vs Venta Total Acumulada
![Gráfica 4](file:///c:/Users/chris/OneDrive/Escritorio/U/2S2026/Geren2/Lab/SOG2-2S26_grupo4/Practica1/graficas_segmentacion/04_scatter_edad_vs_venta_total_regresion.png)

- **Interpretación Técnica:** La nube de 6,500 puntos se distribuye uniformemente en el plano cartesiano. La recta de regresión de mínimos cuadrados (roja) tiene una pendiente casi horizontal ($m = -0.4787$) y un coeficiente de determinación $R^2 = 0.000637$, demostrando independencia lineal entre la edad y el gasto total.

---

### Gráfica 5: Distribución de Métodos de Pago según Género (Heatmap de Contingencia)
![Gráfica 5](file:///c:/Users/chris/OneDrive/Escritorio/U/2S2026/Geren2/Lab/SOG2-2S26_grupo4/Practica1/graficas_segmentacion/05_heatmap_genero_vs_metodo_pago.png)

- **Interpretación Técnica:** El mapa de calor ilustra las proporciones relativas dentro de cada género. Ambos grupos eligen prioritariamente Tarjeta de Crédito (57.74% en mujeres, 59.93% en hombres), seguido por Tarjeta de Débito (~22-23%) y Efectivo (~18-19%). El estadístico $\chi^2 = 3.73$ ($p = 0.1546$) valida que los hábitos de pago son independientes del género.

---

### Gráfica 6: Matriz de Correlación Multivariable Global
![Gráfica 6](file:///c:/Users/chris/OneDrive/Escritorio/U/2S2026/Geren2/Lab/SOG2-2S26_grupo4/Practica1/graficas_segmentacion/06_heatmap_matriz_correlacion_multivariable.png)

- **Interpretación Técnica:** Revela que la variable de mayor correlación con la Venta Total Acumulada es el Número de Compras Históricas ($r = +0.781$). Se identifican correlaciones positivas significativas entre el uso de vales y el monto de compra ($r = +0.129$) y entre boletín y vales ($r = +0.194$).

---

### Gráfica 7: Distribución del Monto de Compra por Cuadrante Promocional (Boxplot)
![Gráfica 7](file:///c:/Users/chris/OneDrive/Escritorio/U/2S2026/Geren2/Lab/SOG2-2S26_grupo4/Practica1/graficas_segmentacion/07_boxplot_monto_compra_por_fidelizacion.png)

- **Interpretación Técnica:** El diagrama de caja y bigotes muestra cómo las cajas intercuartílicas (Q1 a Q3) y los rombos amarillos de la media se desplazan hacia arriba en los cuadrantes con vales ($43.62 y $45.68), evidenciando que el incentivo económico estimula transacciones de mayor cuantía sin generar una dispersión desmedida de outliers negativos.

---

## 6. CONCLUSIONES Y RECOMENDACIONES ESTRATÉGICAS

### 6.1. Conclusiones Clave (Estudiante 4)

1. **Núcleo de Ingresos Concentrado en Millennials (26-40 años):**  
   Aunque el valor promedio de cada transacción es homogéneo en todas las edades (~$40 por compra, ANOVA $p = 0.4193$), más del **52.8% de los ingresos totales** ($136,547 USD) es generado exclusivamente por la cohorte de 26 a 40 años. Esto posiciona a este grupo demográfico como el pilar fundamental para el sostenimiento financiero y la expansión de la empresa.

2. **Homogeneidad de Consumo y Preferencias entre Géneros:**  
   El análisis comparativo entre hombres ($51.8\%$ clientes) y mujeres ($48.1\%$ clientes) reveló que no existen diferencias estadísticamente significativas en el ticket promedio ($39.70 vs $39.88, prueba t $p = 0.7026$), ni en el valor acumulado del cliente ($204.46 vs $208.16), ni en la selección del método de pago ($\chi^2 = 3.73, p = 0.1546$). La oferta de valor de la compañía posee una tracción equilibrada y universal.

3. **Efecto Multiplicador del Vale Promocional en el Tamaño del Ticket:**  
   El uso de vales de descuento demostró ser la variable exógena de mayor impacto positivo en el monto de compra ($F = 38.55, p = 1.10 \times 10^{-24}$). Los clientes que redimieron un vale alcanzaron un ticket medio de **$45.68** (combinado con boletín) y **$43.62** (solo vale), superando en más de un **+19.4%** el ticket medio del cliente orgánico ($38.26).

4. **Sinergia Estratégica entre Boletín Informativo y Conversión de Vales:**  
   Se demostró una relación de adopción cruzada altamente significativa ($\Phi = +0.1940, \chi^2 = 243.57, p < 10^{-50}$). Los suscriptores del boletín tienen un **Odds Ratio de 2.72**, lo que significa que tienen casi el triple de probabilidad de aplicar vales de descuento frente a los no suscritos. El boletín no es solo un canal informativo, sino el catalizador principal de conversión de ofertas.

---

### 6.2. Acciones Concretas Propuestas

1. **Acción 1 — Programa de Onboarding y Captura de Boletín Orientado a la Cohorte 26-40:**  
   Implementar una estrategia de registro al boletín incentivada con un vale de bienvenida para el segmento de 26 a 40 años en la nueva sucursal física y plataforma online. Dado que el Odds Ratio de conversión es de 2.72 y el ticket aumenta a $45.68, la suscripción masiva garantiza un incremento directo en el valor de vida del cliente.

2. **Acción 2 — Pasarela de Pagos Unificada y Beneficios de Tarjeta de Crédito:**  
   Considerando que casi el 60% de los clientes de ambos géneros utiliza tarjeta de crédito, la empresa debe negociar acuerdos con entidades bancarias para ofrecer cuotas sin intereses y programas de lealtad vinculados a la tarjeta de crédito tanto en la tienda física como en la digital, eliminando fricciones en el checkout.
