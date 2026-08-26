-- =============================================================================
-- PRACTICA 1: SISTEMAS ORGANIZACIONALES Y GERENCIALES 2 (2S 2026)
-- ESTUDIANTE 3: ANALISTA EDA Y TENDENCIAS
-- Script SQL para Analisis Exploratorio de Datos (Punto 2) y Tendencias (Punto 3)
-- Base de Datos: PostgreSQL en AWS RDS
-- =============================================================================

-- =============================================================================
-- SECCION 1: ESTADISTICAS BASICAS DE VARIABLES NUMERICAS (Punto 2.b)
-- Variables analizadas: Venta_total, MontoCompra, N_Compras, Edad
-- Metricas: Media (AVG), Mediana (PERCENTILE_CONT 0.50), Moda (MODE), Min, Max, Desv. Estandar
-- =============================================================================

-- 1.1 Estadisticas a nivel de Clientes (Edad, Venta_total acumulada, N_Compras)
SELECT 
    'Edad' AS variable,
    ROUND(AVG(edad), 4) AS media,
    ROUND((PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY edad))::numeric, 4) AS mediana,
    ROUND((MODE() WITHIN GROUP (ORDER BY edad))::numeric, 4) AS moda,
    MIN(edad) AS valor_minimo,
    MAX(edad) AS valor_maximo,
    ROUND(STDDEV(edad), 4) AS desviacion_estandar
FROM clientes
UNION ALL
SELECT 
    'Venta_total (Cliente)' AS variable,
    ROUND(AVG(venta_total), 4) AS media,
    ROUND((PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY venta_total))::numeric, 4) AS mediana,
    ROUND((MODE() WITHIN GROUP (ORDER BY venta_total))::numeric, 4) AS moda,
    MIN(venta_total) AS valor_minimo,
    MAX(venta_total) AS valor_maximo,
    ROUND(STDDEV(venta_total), 4) AS desviacion_estandar
FROM clientes
UNION ALL
SELECT 
    'N_Compras (Cliente)' AS variable,
    ROUND(AVG(n_compras), 4) AS media,
    ROUND((PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY n_compras))::numeric, 4) AS mediana,
    ROUND((MODE() WITHIN GROUP (ORDER BY n_compras))::numeric, 4) AS moda,
    MIN(n_compras) AS valor_minimo,
    MAX(n_compras) AS valor_maximo,
    ROUND(STDDEV(n_compras), 4) AS desviacion_estandar
FROM clientes
UNION ALL
SELECT 
    'MontoCompra (Transaccion)' AS variable,
    ROUND(AVG(monto_compra), 4) AS media,
    ROUND((PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY monto_compra))::numeric, 4) AS mediana,
    ROUND((MODE() WITHIN GROUP (ORDER BY monto_compra))::numeric, 4) AS moda,
    MIN(monto_compra) AS valor_minimo,
    MAX(monto_compra) AS valor_maximo,
    ROUND(STDDEV(monto_compra), 4) AS desviacion_estandar
FROM ventas
UNION ALL
SELECT 
    'Tiempo Sesion Segundos (Transaccion)' AS variable,
    ROUND(AVG(tiempo), 4) AS media,
    ROUND((PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY tiempo))::numeric, 4) AS mediana,
    ROUND((MODE() WITHIN GROUP (ORDER BY tiempo))::numeric, 4) AS moda,
    MIN(tiempo) AS valor_minimo,
    MAX(tiempo) AS valor_maximo,
    ROUND(STDDEV(tiempo), 4) AS desviacion_estandar
FROM ventas;


-- =============================================================================
-- SECCION 2: DISTRIBUCION DE VENTAS (Punto 2.c)
-- Analisis por Metodo de Pago, Navegador, Boletin y Vale
-- =============================================================================

-- 2.1 Distribucion de ventas segun Metodo de Pago
SELECT 
    COALESCE(mp.descripcion, 'Desconocido') AS metodo_pago,
    COUNT(v.id_registro) AS cantidad_transacciones,
    ROUND((COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas)), 2) AS porcentaje_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND((SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas)), 2) AS porcentaje_facturacion,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio,
    ROUND(MIN(v.monto_compra), 2) AS monto_minimo,
    ROUND(MAX(v.monto_compra), 2) AS monto_maximo
FROM ventas v
LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago
GROUP BY mp.descripcion, v.id_metodo_pago
ORDER BY facturacion_total DESC;

-- 2.2 Distribucion de ventas segun Navegador / Canal de Acceso
SELECT 
    COALESCE(nav.descripcion, 'Desconocido') AS canal_navegador,
    COUNT(v.id_registro) AS cantidad_transacciones,
    ROUND((COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas)), 2) AS porcentaje_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND((SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas)), 2) AS porcentaje_facturacion,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio,
    ROUND(AVG(v.tiempo), 2) AS tiempo_promedio_segundos
FROM ventas v
LEFT JOIN cat_navegador nav ON v.id_navegador = nav.id_navegador
GROUP BY nav.descripcion, v.id_navegador
ORDER BY facturacion_total DESC;

-- 2.3 Distribucion de ventas segun Suscripcion al Boletin
SELECT 
    CASE WHEN v.boletin = 1 THEN 'Suscrito a Boletin' ELSE 'No Suscrito' END AS estado_boletin,
    COUNT(v.id_registro) AS cantidad_transacciones,
    ROUND((COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas)), 2) AS porcentaje_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND((SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas)), 2) AS porcentaje_facturacion,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio
FROM ventas v
GROUP BY v.boletin
ORDER BY facturacion_total DESC;

-- 2.4 Distribucion de ventas segun Uso de Vales Promocionales
SELECT 
    CASE WHEN v.vale = 1 THEN 'Aplico Vale' ELSE 'Sin Vale' END AS estado_vale,
    COUNT(v.id_registro) AS cantidad_transacciones,
    ROUND((COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas)), 2) AS porcentaje_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND((SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas)), 2) AS porcentaje_facturacion,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio
FROM ventas v
GROUP BY v.vale
ORDER BY facturacion_total DESC;

-- 2.5 Distribucion cruzada: Boletin x Vale
SELECT 
    CASE WHEN v.boletin = 1 THEN 'Con Boletin' ELSE 'Sin Boletin' END AS boletin_estado,
    CASE WHEN v.vale = 1 THEN 'Con Vale' ELSE 'Sin Vale' END AS vale_estado,
    COUNT(v.id_registro) AS cantidad_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio
FROM ventas v
GROUP BY v.boletin, v.vale
ORDER BY facturacion_total DESC;


-- =============================================================================
-- SECCION 3: IDENTIFICACION DE TENDENCIAS (Punto 3 del alcance)
-- =============================================================================

-- 3.1 Tendencias mensuales: Meses con mayores y menores ventas (Punto 3.a)
WITH ventas_mensuales AS (
    SELECT 
        TO_CHAR(v.fecha_compra, 'YYYY-MM') AS periodo_mes,
        EXTRACT(MONTH FROM v.fecha_compra) AS numero_mes,
        TO_CHAR(v.fecha_compra, 'TMMonth') AS nombre_mes,
        COUNT(v.id_registro) AS total_transacciones,
        ROUND(SUM(v.monto_compra), 2) AS total_facturado,
        ROUND(AVG(v.monto_compra), 2) AS ticket_promedio
    FROM ventas v
    GROUP BY TO_CHAR(v.fecha_compra, 'YYYY-MM'), EXTRACT(MONTH FROM v.fecha_compra), TO_CHAR(v.fecha_compra, 'TMMonth')
)
SELECT 
    periodo_mes,
    TRIM(nombre_mes) AS mes,
    total_transacciones,
    total_facturado,
    ticket_promedio,
    RANK() OVER (ORDER BY total_facturado DESC) AS ranking_mayor_venta,
    RANK() OVER (ORDER BY total_facturado ASC) AS ranking_menor_venta
FROM ventas_mensuales
ORDER BY total_facturado DESC;

-- 3.2 Mes con MAYOR y MENOR venta puntualmente
(
    SELECT 
        'Mes con Mayor Venta' AS tipo_tendencia,
        TO_CHAR(fecha_compra, 'YYYY-MM') AS periodo,
        COUNT(id_registro) AS transacciones,
        ROUND(SUM(monto_compra), 2) AS monto_total
    FROM ventas
    GROUP BY TO_CHAR(fecha_compra, 'YYYY-MM')
    ORDER BY monto_total DESC
    LIMIT 1
)
UNION ALL
(
    SELECT 
        'Mes con Menor Venta' AS tipo_tendencia,
        TO_CHAR(fecha_compra, 'YYYY-MM') AS periodo,
        COUNT(id_registro) AS transacciones,
        ROUND(SUM(monto_compra), 2) AS monto_total
    FROM ventas
    GROUP BY TO_CHAR(fecha_compra, 'YYYY-MM')
    ORDER BY monto_total ASC
    LIMIT 1
);

-- 3.3 Navegador de Internet mas y menos utilizado (Punto 3.b)
-- Se analizan tanto canales totales como especificamente navegadores web (id_navegador >= 1)
WITH ranking_navegadores AS (
    SELECT 
        v.id_navegador,
        COALESCE(nav.descripcion, 'Desconocido') AS nombre_navegador,
        COUNT(v.id_registro) AS total_usuarios_sesiones,
        ROUND(SUM(v.monto_compra), 2) AS monto_total,
        ROUND((COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas)), 2) AS porcentaje_uso
    FROM ventas v
    LEFT JOIN cat_navegador nav ON v.id_navegador = nav.id_navegador
    GROUP BY v.id_navegador, nav.descripcion
)
SELECT 
    id_navegador,
    nombre_navegador,
    total_usuarios_sesiones,
    monto_total,
    porcentaje_uso,
    RANK() OVER (ORDER BY total_usuarios_sesiones DESC) AS ranking_popularidad
FROM ranking_navegadores
ORDER BY total_usuarios_sesiones DESC;

-- 3.4 Total de ventas en efectivo o pago contra entrega (MetodoPago = 0) (Punto 3.c)
SELECT 
    v.id_metodo_pago,
    COALESCE(mp.descripcion, 'Efectivo') AS descripcion_metodo,
    COUNT(v.id_registro) AS total_transacciones_efectivo,
    ROUND(SUM(v.monto_compra), 2) AS monto_total_efectivo,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio_efectivo,
    ROUND((COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas)), 2) AS pct_sobre_total_transacciones,
    ROUND((SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas)), 2) AS pct_sobre_facturacion_global
FROM ventas v
LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago
WHERE v.id_metodo_pago = 0
GROUP BY v.id_metodo_pago, mp.descripcion;

-- 3.5 Meses con mayor adopcion de boletines y vales promocionales (Punto 3.d)
SELECT 
    TO_CHAR(v.fecha_compra, 'YYYY-MM') AS periodo_mes,
    COUNT(v.id_registro) AS total_transacciones_mes,
    SUM(CASE WHEN v.boletin = 1 THEN 1 ELSE 0 END) AS total_adopcion_boletin,
    ROUND((SUM(CASE WHEN v.boletin = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(v.id_registro)), 2) AS pct_boletin_en_mes,
    SUM(CASE WHEN v.vale = 1 THEN 1 ELSE 0 END) AS total_adopcion_vales,
    ROUND((SUM(CASE WHEN v.vale = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(v.id_registro)), 2) AS pct_vales_en_mes,
    SUM(CASE WHEN v.boletin = 1 AND v.vale = 1 THEN 1 ELSE 0 END) AS total_ambos
FROM ventas v
GROUP BY TO_CHAR(v.fecha_compra, 'YYYY-MM')
ORDER BY total_adopcion_vales DESC, total_adopcion_boletin DESC;
