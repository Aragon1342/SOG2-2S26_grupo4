-- =====================================================================================
-- Conexión a la Base de Datos de Odoo:
--   Gestor Web BD: Servidor web de base de datos
--   Motor:        PostgreSQL
--   Database:     quetzalmart
-- =====================================================================================

-- -------------------------------------------------------------------------------------
-- SECCIÓN 1: COMPROBACIÓN DE CLIENTES (res_partner)
-- -------------------------------------------------------------------------------------

-- 1.1 Conteo total de clientes cargados por el RPA (filtrando por External ID del RPA)
SELECT 
    COUNT(p.id) AS total_clientes_rpa
FROM res_partner p
JOIN ir_model_data imd ON imd.model = 'res.partner' AND imd.res_id = p.id
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'cust%')
  AND imd.module = '__import__';

-- 1.2 Detalle de clientes cargados clasificados por tipo (Empresa vs Contacto individual)
SELECT 
    imd.name AS id_externo,
    p.id AS id_interno_odoo,
    p.name AS nombre_cliente,
    CASE 
        WHEN p.is_company = TRUE THEN 'Empresa'
        ELSE 'Contacto / Persona'
    END AS tipo_entidad,
    padre.name AS empresa_relacionada,
    p.email,
    p.phone AS telefono,
    p.street AS direccion,
    p.city AS ciudad,
    p.zip AS codigo_postal,
    p.vat AS nit_tax_id,
    p.ref AS referencia_interna,
    p.comment AS notas,
    p.create_date AS fecha_creacion
FROM res_partner p
JOIN ir_model_data imd ON imd.model = 'res.partner' AND imd.res_id = p.id
LEFT JOIN res_partner padre ON p.parent_id = padre.id
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'cust%')
  AND imd.module = '__import__'
ORDER BY p.is_company DESC, p.name ASC;

-- 1.3 Verificación de relaciones Padre-Hijo (Empresa y sus Contactos asociados)
SELECT 
    padre.name AS empresa,
    hijo.name AS contacto_asociado,
    hijo.email AS correo_contacto,
    hijo.phone AS telefono_contacto
FROM res_partner hijo
JOIN res_partner padre ON hijo.parent_id = padre.id
JOIN ir_model_data imd ON imd.model = 'res.partner' AND imd.res_id = hijo.id
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'cust%')
  AND imd.module = '__import__';


-- -------------------------------------------------------------------------------------
-- SECCIÓN 2: COMPROBACIÓN DE PRODUCTOS (product_template y product_product)
-- -------------------------------------------------------------------------------------

-- 2.1 Conteo total de productos importados y resumen por estado publicado / tipo
SELECT 
    pt.detailed_type AS tipo_producto,
    COALESCE(pt.is_published, FALSE) AS esta_publicado,
    COUNT(pt.id) AS cantidad_productos
FROM product_template pt
JOIN ir_model_data imd ON imd.model = 'product.template' AND imd.res_id = pt.id
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'prueba_product%')
  AND imd.module = '__import__'
GROUP BY pt.detailed_type, COALESCE(pt.is_published, FALSE);

-- 2.2 Lista completa de productos importados con precios, códigos de barra y publicación
SELECT 
    imd.name AS id_externo,
    pt.id AS template_id,
    pt.name AS nombre_producto,
    pt.detailed_type AS tipo,
    pt.default_code AS referencia_interna,
    pt.barcode AS codigo_barras,
    pt.list_price AS precio_venta_quetzales,
    pt.standard_price AS costo_quetzales,
    pt.weight AS peso_kg,
    COALESCE(pt.is_published, FALSE) AS publicado_en_web,
    pt.create_date AS fecha_registro
FROM product_template pt
JOIN ir_model_data imd ON imd.model = 'product.template' AND imd.res_id = pt.id
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'prueba_product%')
  AND imd.module = '__import__'
ORDER BY pt.name ASC;

-- 2.3 Verificación específica de productos PUBLICADOS vs NO PUBLICADOS
SELECT 
    pt.name AS producto,
    pt.list_price AS precio,
    CASE 
        WHEN COALESCE(pt.is_published, FALSE) = TRUE THEN 'VISIBLE EN TIENDA WEB'
        ELSE 'OCULTO EN TIENDA WEB (NO PUBLICADO)'
    END AS visibilidad_ecommerce
FROM product_template pt
JOIN ir_model_data imd ON imd.model = 'product.template' AND imd.res_id = pt.id
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'prueba_product%')
  AND imd.module = '__import__'
ORDER BY visibilidad_ecommerce DESC, pt.name ASC;


-- -------------------------------------------------------------------------------------
-- SECCIÓN 3: COMPROBACIÓN DE INVENTARIO Y CANTIDAD A LA MANO (stock_quant)
-- -------------------------------------------------------------------------------------

-- 3.1 Consulta de existencias físicas (Cantidad a la mano) por producto y ubicación
SELECT 
    pt.name AS producto,
    pt.default_code AS referencia,
    loc.complete_name AS ubicacion,
    sq.quantity AS cantidad_a_la_mano,
    sq.in_date AS fecha_ingreso
FROM stock_quant sq
JOIN product_product pp ON sq.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
JOIN stock_location loc ON sq.location_id = loc.id
WHERE loc.usage = 'internal'
  AND sq.quantity > 0
ORDER BY sq.quantity DESC;

-- 3.2 Comparativa cruzada: Precios, Existencias e Importe Total de Inventario
SELECT 
    pt.name AS producto,
    pt.default_code AS sku,
    sq.quantity AS existencias_stock,
    pt.list_price AS precio_venta_unitario,
    pt.standard_price AS costo_unitario,
    (sq.quantity * pt.standard_price) AS valor_total_costo,
    (sq.quantity * pt.list_price) AS valor_potencial_venta
FROM stock_quant sq
JOIN product_product pp ON sq.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
JOIN stock_location loc ON sq.location_id = loc.id
WHERE loc.usage = 'internal'
ORDER BY valor_total_costo DESC;


-- -------------------------------------------------------------------------------------
-- SECCIÓN 4: CONSULTA RESUMEN PARA PRESENTACIÓN AL AUXILIAR (DASHBOARD SQL)
-- -------------------------------------------------------------------------------------
SELECT 
    'Clientes Empresas' AS categoria, COUNT(*) AS total 
FROM res_partner p 
JOIN ir_model_data imd ON imd.model='res.partner' AND imd.res_id=p.id 
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'cust%')
  AND imd.module = '__import__'
  AND p.is_company = TRUE
UNION ALL
SELECT 
    'Clientes Contactos/Personas' AS categoria, COUNT(*) AS total 
FROM res_partner p 
JOIN ir_model_data imd ON imd.model='res.partner' AND imd.res_id=p.id 
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'cust%')
  AND imd.module = '__import__'
  AND p.is_company = FALSE
UNION ALL
SELECT 
    'Productos Totales' AS categoria, COUNT(*) AS total 
FROM product_template pt 
JOIN ir_model_data imd ON imd.model='product.template' AND imd.res_id=pt.id 
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'prueba_product%')
  AND imd.module = '__import__'
UNION ALL
SELECT 
    'Productos Publicados en Web' AS categoria, COUNT(*) AS total 
FROM product_template pt 
JOIN ir_model_data imd ON imd.model='product.template' AND imd.res_id=pt.id 
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'prueba_product%')
  AND imd.module = '__import__'
  AND COALESCE(pt.is_published, FALSE) = TRUE
UNION ALL
SELECT 
    'Productos No Publicados' AS categoria, COUNT(*) AS total 
FROM product_template pt 
JOIN ir_model_data imd ON imd.model='product.template' AND imd.res_id=pt.id 
WHERE (LOWER(imd.name) LIKE 'qm_%' OR LOWER(imd.name) LIKE 'prueba_product%')
  AND imd.module = '__import__'
  AND COALESCE(pt.is_published, FALSE) = FALSE
UNION ALL
SELECT 
    'Unidades Físicas en Stock (Cantidad a la mano)' AS categoria, CAST(SUM(quantity) AS BIGINT) AS total 
FROM stock_quant sq 
JOIN stock_location loc ON sq.location_id=loc.id 
WHERE loc.usage='internal';
