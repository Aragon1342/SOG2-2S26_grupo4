-- =============================================================================
-- PRÁCTICA 1: SISTEMAS ORGANIZACIONALES Y GERENCIALES 2 (2S 2026)
-- Esquema Relacional Normalizado / Modelo Dimensional para AWS RDS (PostgreSQL)
-- =============================================================================

-- Eliminar tablas previas si existen en cascada para recrear limpiamente
DROP TABLE IF EXISTS ventas CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS cat_genero CASCADE;
DROP TABLE IF EXISTS cat_metodo_pago CASCADE;
DROP TABLE IF EXISTS cat_navegador CASCADE;

-- -----------------------------------------------------------------------------
-- 1. TABLAS DE CATÁLOGO / DIMENSIONES (LOOKUP TABLES)
-- -----------------------------------------------------------------------------

-- Catálogo de Géneros
CREATE TABLE cat_genero (
    id_genero    SMALLINT PRIMARY KEY,
    descripcion  VARCHAR(20) NOT NULL
);

INSERT INTO cat_genero (id_genero, descripcion) VALUES
    (0, 'Masculino'),
    (1, 'Femenino')
ON CONFLICT (id_genero) DO NOTHING;


-- Catálogo de Métodos de Pago
CREATE TABLE cat_metodo_pago (
    id_metodo_pago  SMALLINT PRIMARY KEY,
    descripcion     VARCHAR(50) NOT NULL
);

INSERT INTO cat_metodo_pago (id_metodo_pago, descripcion) VALUES
    (0, 'Efectivo'),
    (1, 'Tarjeta de Crédito'),
    (2, 'Tarjeta de Débito')
ON CONFLICT (id_metodo_pago) DO NOTHING;


-- Catálogo de Canales / Navegadores
CREATE TABLE cat_navegador (
    id_navegador  SMALLINT PRIMARY KEY,
    descripcion   VARCHAR(50) NOT NULL
);

INSERT INTO cat_navegador (id_navegador, descripcion) VALUES
    (0, 'Tienda Física'),
    (1, 'Navegador 1'),
    (2, 'Navegador 2'),
    (3, 'Navegador 3'),
    (4, 'Navegador 4')
ON CONFLICT (id_navegador) DO NOTHING;


-- -----------------------------------------------------------------------------
-- 2. TABLA MAESTRA DE CLIENTES
-- -----------------------------------------------------------------------------
CREATE TABLE clientes (
    id_cliente   INTEGER PRIMARY KEY,
    edad         INTEGER,
    id_genero    SMALLINT,
    venta_total  NUMERIC(12, 2),
    n_compras    INTEGER,
    CONSTRAINT fk_cliente_genero FOREIGN KEY (id_genero) 
        REFERENCES cat_genero(id_genero) ON DELETE SET NULL
);

CREATE INDEX idx_clientes_genero ON clientes (id_genero);


-- -----------------------------------------------------------------------------
-- 3. TABLA TRANSACCIONAL DE VENTAS (TABLA DE HECHOS)
-- -----------------------------------------------------------------------------
CREATE TABLE ventas (
    id_registro     SERIAL PRIMARY KEY,
    id_cliente      INTEGER NOT NULL,
    fecha_compra    DATE NOT NULL,
    monto_compra    NUMERIC(12, 3),
    id_metodo_pago  SMALLINT,
    id_navegador    SMALLINT,
    tiempo          NUMERIC(10, 2),
    boletin         SMALLINT CHECK (boletin IN (0, 1)),
    vale            SMALLINT CHECK (vale IN (0, 1)),
    CONSTRAINT fk_ventas_cliente FOREIGN KEY (id_cliente) 
        REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    CONSTRAINT fk_ventas_metodo_pago FOREIGN KEY (id_metodo_pago) 
        REFERENCES cat_metodo_pago(id_metodo_pago) ON DELETE SET NULL,
    CONSTRAINT fk_ventas_navegador FOREIGN KEY (id_navegador) 
        REFERENCES cat_navegador(id_navegador) ON DELETE SET NULL
);

CREATE INDEX idx_ventas_cliente ON ventas (id_cliente);
CREATE INDEX idx_ventas_fecha_compra ON ventas (fecha_compra);
CREATE INDEX idx_ventas_metodo_pago ON ventas (id_metodo_pago);
CREATE INDEX idx_ventas_navegador ON ventas (id_navegador);


-- -----------------------------------------------------------------------------
-- 4. DICCIONARIO DE DATOS (COMENTARIOS EN POSTGRESQL)
-- -----------------------------------------------------------------------------
COMMENT ON TABLE cat_genero IS 'Catálogo maestro de géneros de clientes';
COMMENT ON TABLE cat_metodo_pago IS 'Catálogo de formas de pago aceptadas';
COMMENT ON TABLE cat_navegador IS 'Catálogo de canales y navegadores de acceso a tienda';
COMMENT ON TABLE clientes IS 'Dimensión de clientes con métricas acumuladas';
COMMENT ON TABLE ventas IS 'Tabla de hechos transaccionales de ventas 2021';


-- -----------------------------------------------------------------------------
-- 5. VISTAS ANALÍTICAS GERENCIALES
-- -----------------------------------------------------------------------------

-- Vista desnormalizada con nombres legibles para reportes e IA
CREATE OR REPLACE VIEW vista_ventas_completa AS
SELECT 
    v.id_registro,
    v.id_cliente,
    c.edad,
    g.descripcion AS genero,
    c.venta_total AS venta_total_acumulada_cliente,
    c.n_compras AS compras_historicas_cliente,
    v.fecha_compra,
    v.monto_compra,
    mp.descripcion AS metodo_pago,
    v.tiempo AS tiempo_sesion_segundos,
    nav.descripcion AS canal_navegador,
    CASE WHEN v.boletin = 1 THEN 'Suscrito' ELSE 'No Suscrito' END AS estado_boletin,
    CASE WHEN v.vale = 1 THEN 'Aplicó Vale' ELSE 'Sin Vale' END AS estado_vale
FROM ventas v
LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
LEFT JOIN cat_genero g ON c.id_genero = g.id_genero
LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago
LEFT JOIN cat_navegador nav ON v.id_navegador = nav.id_navegador;


-- Vista resumen mensual para análisis ejecutivo
CREATE OR REPLACE VIEW vista_resumen_gerencial AS
SELECT 
    DATE_TRUNC('month', v.fecha_compra)::DATE AS mes,
    COUNT(v.id_registro) AS total_transacciones,
    COUNT(DISTINCT v.id_cliente) AS clientes_unicos,
    ROUND(SUM(v.monto_compra), 2) AS facturacion_total,
    ROUND(AVG(v.monto_compra), 2) AS ticket_promedio,
    ROUND(AVG(v.tiempo), 2) AS tiempo_promedio_navegacion
FROM ventas v
GROUP BY DATE_TRUNC('month', v.fecha_compra)
ORDER BY mes;
