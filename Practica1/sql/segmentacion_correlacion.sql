-- =============================================================================
-- PRACTICA 1: SISTEMAS ORGANIZACIONALES Y GERENCIALES 2 (2S 2026)
-- ESTUDIANTE 4: ANALISTA DE SEGMENTACION Y CORRELACIONES
-- Script SQL para Segmentacion de Clientes (Punto 4) y Correlaciones (Punto 5)
-- Base de Datos: PostgreSQL en AWS RDS
-- =============================================================================

-- =============================================================================
-- SECCION 1: SEGMENTACION DE CLIENTES (Punto 4 del Alcance)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 4.a Segmentacion de Clientes por Rango de Edad
-- Analiza habitos de compra: Cantidad de clientes, volumen total de ventas,
-- ticket promedio, numero de compras promedio y tiempo de sesion promedio.
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN c.edad BETWEEN 18 AND 25 THEN '1. 18-25 (Joven / Gen Z)'
        WHEN c.edad BETWEEN 26 AND 40 THEN '2. 26-40 (Adulto Joven / Millennial)'
        WHEN c.edad BETWEEN 41 AND 55 THEN '3. 41-55 (Adulto / Gen X)'
        WHEN c.edad >= 56             THEN '4. 56+ (Adulto Mayor / Boomer)'
        ELSE 'Desconocido'
    END AS rango_edad,
    COUNT(DISTINCT c.id_cliente) AS total_clientes,
    ROUND(COUNT(DISTINCT c.id_cliente) * 100.0 / (SELECT COUNT(*) FROM clientes), 2) AS pct_clientes,
    COUNT(v.id_registro) AS total_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND(SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas), 2) AS pct_facturacion,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio,
    ROUND(AVG(c.n_compras), 2) AS promedio_compras_historicas,
    ROUND(AVG(v.tiempo), 2) AS tiempo_promedio_navegacion_seg,
    ROUND(MIN(v.monto_compra), 2) AS compra_minima,
    ROUND(MAX(v.monto_compra), 2) AS compra_maxima
FROM clientes c
LEFT JOIN ventas v ON c.id_cliente = v.id_cliente
GROUP BY 
    CASE 
        WHEN c.edad BETWEEN 18 AND 25 THEN '1. 18-25 (Joven / Gen Z)'
        WHEN c.edad BETWEEN 26 AND 40 THEN '2. 26-40 (Adulto Joven / Millennial)'
        WHEN c.edad BETWEEN 41 AND 55 THEN '3. 41-55 (Adulto / Gen X)'
        WHEN c.edad >= 56             THEN '4. 56+ (Adulto Mayor / Boomer)'
        ELSE 'Desconocido'
    END
ORDER BY rango_edad;


-- -----------------------------------------------------------------------------
-- 4.b Comparativa de Comportamiento de Compra Segun Genero (Genero 0 vs 1)
-- Compara el desempeno comercial entre Masculino (0) y Femenino (1)
-- -----------------------------------------------------------------------------
SELECT 
    COALESCE(g.descripcion, 'No Especificado') AS genero,
    c.id_genero,
    COUNT(DISTINCT c.id_cliente) AS total_clientes,
    ROUND(COUNT(DISTINCT c.id_cliente) * 100.0 / (SELECT COUNT(*) FROM clientes), 2) AS pct_clientes,
    COUNT(v.id_registro) AS total_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND(SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas), 2) AS pct_facturacion,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio,
    ROUND(STDDEV(v.monto_compra), 2) AS desviacion_ticket,
    ROUND(AVG(c.venta_total), 2) AS ltv_promedio_cliente,
    ROUND(AVG(c.n_compras), 2) AS compras_historicas_promedio,
    ROUND(AVG(v.tiempo), 2) AS tiempo_promedio_segundos
FROM clientes c
LEFT JOIN cat_genero g ON c.id_genero = g.id_genero
LEFT JOIN ventas v ON c.id_cliente = v.id_cliente
GROUP BY g.descripcion, c.id_genero
ORDER BY c.id_genero;


-- -----------------------------------------------------------------------------
-- 4.c Segmentacion de Clientes por Uso de Boletin y Vales Promocionales
-- Evalua 4 cuadrantes: 
-- 1. Ambos (Boletin + Vale), 2. Solo Boletin, 3. Solo Vale, 4. Ninguno
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN v.boletin = 1 AND v.vale = 1 THEN '1. Ambos (Boletín y Vale)'
        WHEN v.boletin = 1 AND v.vale = 0 THEN '2. Solo Boletín'
        WHEN v.boletin = 0 AND v.vale = 1 THEN '3. Solo Vale'
        WHEN v.boletin = 0 AND v.vale = 0 THEN '4. Ninguno (Orgánico/Sin Promo)'
        ELSE 'Otro'
    END AS segmento_fidelizacion,
    COUNT(v.id_registro) AS total_transacciones,
    ROUND(COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas), 2) AS pct_transacciones,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND(SUM(v.monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas), 2) AS pct_facturacion,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio,
    ROUND(STDDEV(v.monto_compra), 2) AS desviacion_ticket,
    ROUND(AVG(v.tiempo), 2) AS tiempo_promedio_segundos,
    ROUND(MIN(v.monto_compra), 2) AS monto_minimo,
    ROUND(MAX(v.monto_compra), 2) AS monto_maximo
FROM ventas v
GROUP BY 
    CASE 
        WHEN v.boletin = 1 AND v.vale = 1 THEN '1. Ambos (Boletín y Vale)'
        WHEN v.boletin = 1 AND v.vale = 0 THEN '2. Solo Boletín'
        WHEN v.boletin = 0 AND v.vale = 1 THEN '3. Solo Vale'
        WHEN v.boletin = 0 AND v.vale = 0 THEN '4. Ninguno (Orgánico/Sin Promo)'
        ELSE 'Otro'
    END
ORDER BY segmento_fidelizacion;


-- =============================================================================
-- SECCION 2: ANALISIS DE CORRELACION Y PRUEBAS ESTADISTICAS (Punto 5 del Alcance)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 5.a Correlacion entre Edad del Cliente y Venta Total Acumulada / Monto Compra
-- Utiliza funciones estadisticas nativas de PostgreSQL:
-- CORR() -> Coeficiente de correlacion de Pearson
-- REGR_SLOPE() -> Pendiente de la recta de regresion
-- REGR_INTERCEPT() -> Intercepto de la recta de regresion
-- REGR_R2() -> Coeficiente de determinacion R^2
-- -----------------------------------------------------------------------------
SELECT 
    'Edad vs Venta Total Acumulada (Nivel Clientes)' AS relacion_analizada,
    COUNT(*) AS total_observaciones,
    ROUND(CORR(c.edad, c.venta_total)::numeric, 4) AS coeficiente_pearson_r,
    ROUND(REGR_R2(c.venta_total, c.edad)::numeric, 6) AS coeficiente_r2,
    ROUND(REGR_SLOPE(c.venta_total, c.edad)::numeric, 4) AS pendiente_regresion_m,
    ROUND(REGR_INTERCEPT(c.venta_total, c.edad)::numeric, 4) AS intercepto_regresion_b,
    ROUND(AVG(c.edad)::numeric, 2) AS media_edad,
    ROUND(AVG(c.venta_total)::numeric, 2) AS media_venta_total
FROM clientes c
WHERE c.edad IS NOT NULL AND c.venta_total IS NOT NULL
UNION ALL
SELECT 
    'Edad vs Monto de Compra Transaccional (Nivel Ventas)' AS relacion_analizada,
    COUNT(*) AS total_observaciones,
    ROUND(CORR(c.edad, v.monto_compra)::numeric, 4) AS coeficiente_pearson_r,
    ROUND(REGR_R2(v.monto_compra, c.edad)::numeric, 6) AS coeficiente_r2,
    ROUND(REGR_SLOPE(v.monto_compra, c.edad)::numeric, 4) AS pendiente_regresion_m,
    ROUND(REGR_INTERCEPT(v.monto_compra, c.edad)::numeric, 4) AS intercepto_regresion_b,
    ROUND(AVG(c.edad)::numeric, 2) AS media_edad,
    ROUND(AVG(v.monto_compra)::numeric, 2) AS media_monto_compra
FROM ventas v
JOIN clientes c ON v.id_cliente = c.id_cliente
WHERE c.edad IS NOT NULL AND v.monto_compra IS NOT NULL;


-- -----------------------------------------------------------------------------
-- 5.b Tabla de Contingencia y Distribucion: Genero vs Metodo de Pago
-- Evalua si el metodo de pago seleccionado depende del genero del cliente.
-- -----------------------------------------------------------------------------
SELECT 
    COALESCE(g.descripcion, 'Sin Genero') AS genero,
    COALESCE(mp.descripcion, 'Sin Metodo') AS metodo_pago,
    COUNT(v.id_registro) AS frecuencia_observada,
    ROUND(COUNT(v.id_registro) * 100.0 / SUM(COUNT(v.id_registro)) OVER(PARTITION BY g.descripcion), 2) AS pct_dentro_del_genero,
    ROUND(COUNT(v.id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas), 2) AS pct_total_general,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio
FROM ventas v
JOIN clientes c ON v.id_cliente = c.id_cliente
LEFT JOIN cat_genero g ON c.id_genero = g.id_genero
LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago
GROUP BY g.descripcion, mp.descripcion, g.id_genero, mp.id_metodo_pago
ORDER BY g.descripcion, mp.descripcion;

-- Vista pivotada de contingencia Genero x Metodo de Pago
SELECT 
    COALESCE(g.descripcion, 'Sin Genero') AS genero,
    COUNT(CASE WHEN v.id_metodo_pago = 0 THEN 1 END) AS efectivo_obs,
    COUNT(CASE WHEN v.id_metodo_pago = 1 THEN 1 END) AS tarjeta_credito_obs,
    COUNT(CASE WHEN v.id_metodo_pago = 2 THEN 1 END) AS tarjeta_debito_obs,
    COUNT(*) AS total_genero
FROM ventas v
JOIN clientes c ON v.id_cliente = c.id_cliente
LEFT JOIN cat_genero g ON c.id_genero = g.id_genero
GROUP BY g.descripcion, g.id_genero
ORDER BY g.id_genero;


-- -----------------------------------------------------------------------------
-- 5.c Matriz de Contingencia y Correlacion: Uso de Boletin vs Uso de Vales
-- Evalua la relacion de adopcion cruzada entre herramientas promocionales.
-- -----------------------------------------------------------------------------
SELECT 
    CASE WHEN v.boletin = 1 THEN 'Suscrito a Boletín' ELSE 'No Suscrito' END AS estado_boletin,
    COUNT(CASE WHEN v.vale = 1 THEN 1 END) AS uso_vale_si,
    COUNT(CASE WHEN v.vale = 0 THEN 1 END) AS uso_vale_no,
    COUNT(*) AS total_por_boletin,
    ROUND(COUNT(CASE WHEN v.vale = 1 THEN 1 END) * 100.0 / COUNT(*), 2) AS tasa_conversion_vale_pct
FROM ventas v
GROUP BY v.boletin
ORDER BY v.boletin DESC;

-- Calculo de correlacion de Pearson / Coeficiente Phi entre Boletin y Vale en SQL
SELECT 
    'Boletín vs Vale Promocional' AS relacion_binaria,
    ROUND(CORR(boletin, vale)::numeric, 4) AS coeficiente_phi_pearson,
    COUNT(*) AS total_transacciones,
    SUM(CASE WHEN boletin = 1 AND vale = 1 THEN 1 ELSE 0 END) AS a_ambos_1_1,
    SUM(CASE WHEN boletin = 1 AND vale = 0 THEN 1 ELSE 0 END) AS b_boletin_solo_1_0,
    SUM(CASE WHEN boletin = 0 AND vale = 1 THEN 1 ELSE 0 END) AS c_vale_solo_0_1,
    SUM(CASE WHEN boletin = 0 AND vale = 0 THEN 1 ELSE 0 END) AS d_ninguno_0_0
FROM ventas;


-- -----------------------------------------------------------------------------
-- 5.d Matriz de Correlaciones Multivariables en PostgreSQL
-- Correlacion de Pearson entre variables continuas y transaccionales
-- -----------------------------------------------------------------------------
SELECT 
    'Edad vs Tiempo Sesión' AS par_variables,
    ROUND(CORR(c.edad, v.tiempo)::numeric, 4) AS correlacion_pearson
FROM ventas v JOIN clientes c ON v.id_cliente = c.id_cliente
UNION ALL
SELECT 
    'Monto Compra vs Tiempo Sesión',
    ROUND(CORR(v.monto_compra, v.tiempo)::numeric, 4)
FROM ventas v
UNION ALL
SELECT 
    'Monto Compra vs N_Compras Históricas',
    ROUND(CORR(v.monto_compra, c.n_compras)::numeric, 4)
FROM ventas v JOIN clientes c ON v.id_cliente = c.id_cliente
UNION ALL
SELECT 
    'Venta Total Acumulada vs N_Compras Históricas',
    ROUND(CORR(c.venta_total, c.n_compras)::numeric, 4)
FROM clientes c
UNION ALL
SELECT 
    'Monto Compra vs Uso de Vale',
    ROUND(CORR(v.monto_compra, v.vale)::numeric, 4)
FROM ventas v
UNION ALL
SELECT 
    'Monto Compra vs Suscripción Boletín',
    ROUND(CORR(v.monto_compra, v.boletin)::numeric, 4)
FROM ventas v;
