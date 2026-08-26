"""
ETL Pipeline - Práctica 1: Sistemas Organizacionales y Gerenciales 2 (2S2026)
-----------------------------------------------------------------------------
Este script realiza el proceso de Extracción, Transformación y Carga (ETL)
hacia un Modelo Relacional Normalizado / Estrella en AWS RDS PostgreSQL:

Tablas del Modelo:
1. cat_genero (id_genero, descripcion)
2. cat_metodo_pago (id_metodo_pago, descripcion)
3. cat_navegador (id_navegador, descripcion)
4. clientes (id_cliente, edad, id_genero, venta_total, n_compras)
5. ventas (id_registro, id_cliente, fecha_compra, monto_compra, id_metodo_pago, id_navegador, tiempo, boletin, vale)
"""

import os
import sys
import argparse
import logging
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

import pathlib
# Cargar variables de entorno desde .env de Practica1
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ETL_Practica1")

# Mapeo de columnas esperadas en el archivo CSV
EXPECTED_COLUMNS = {
    'id_cliente': 'id_cliente',
    'edad': 'edad',
    'genero': 'id_genero',
    'id_genero': 'id_genero',
    'venta_total': 'venta_total',
    'n_compras': 'n_compras',
    'fechacompra': 'fecha_compra',
    'fecha_compra': 'fecha_compra',
    'montocompra': 'monto_compra',
    'monto_compra': 'monto_compra',
    'metodopago': 'id_metodo_pago',
    'metodo_pago': 'id_metodo_pago',
    'id_metodo_pago': 'id_metodo_pago',
    'tiempo': 'tiempo',
    'navegador': 'id_navegador',
    'id_navegador': 'id_navegador',
    'boletin': 'boletin',
    'boletín': 'boletin',
    'vale': 'vale'
}


def get_db_engine(db_url: Optional[str] = None):
    """
    Crea y retorna el motor de SQLAlchemy conectado a la base de datos.
    """
    connection_string = db_url or os.getenv("DATABASE_URL")
    if not connection_string:
        default_sqlite = "sqlite:///practica1_local.db"
        logger.warning(f"No se proporcionó DATABASE_URL en .env. Usando SQLite local: {default_sqlite}")
        connection_string = default_sqlite
    
    if connection_string.startswith("postgres://"):
        connection_string = connection_string.replace("postgres://", "postgresql://", 1)

    try:
        engine = create_engine(connection_string, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Conexión exitosa a la base de datos: {engine.url.drivername}://{engine.url.host or 'local'}")
        return engine
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise


def init_database_schema(engine, drop_existing: bool = False):
    """
    Crea las tablas maestras, catálogos, relaciones e índices si no existen.
    Si drop_existing es True, elimina las tablas previas en cascada para recrear limpiamente.
    """
    logger.info("Inicializando esquema de base de datos relacional...")
    is_sqlite = engine.url.drivername.startswith("sqlite")
    
    with engine.begin() as conn:
        if drop_existing:
            logger.info("Eliminando tablas anteriores si existen para aplicar nuevo modelo normalizado...")
            if not is_sqlite:
                conn.execute(text("DROP VIEW IF EXISTS vista_ventas_completa CASCADE;"))
                conn.execute(text("DROP VIEW IF EXISTS vista_resumen_gerencial CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS ventas CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS clientes CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS cat_genero CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS cat_metodo_pago CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS cat_navegador CASCADE;"))
            else:
                conn.execute(text("DROP TABLE IF EXISTS ventas;"))
                conn.execute(text("DROP TABLE IF EXISTS clientes;"))
                conn.execute(text("DROP TABLE IF EXISTS cat_genero;"))
                conn.execute(text("DROP TABLE IF EXISTS cat_metodo_pago;"))
                conn.execute(text("DROP TABLE IF EXISTS cat_navegador;"))

        # Catálogo de Género
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cat_genero (
                id_genero SMALLINT PRIMARY KEY,
                descripcion VARCHAR(20) NOT NULL
            );
        """))

        # Catálogo de Métodos de Pago
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cat_metodo_pago (
                id_metodo_pago SMALLINT PRIMARY KEY,
                descripcion VARCHAR(50) NOT NULL
            );
        """))

        # Catálogo de Navegadores / Canales
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cat_navegador (
                id_navegador SMALLINT PRIMARY KEY,
                descripcion VARCHAR(50) NOT NULL
            );
        """))

        # Tabla Maestra de Clientes
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY,
                edad INTEGER,
                id_genero SMALLINT,
                venta_total NUMERIC(12, 2),
                n_compras INTEGER,
                FOREIGN KEY (id_genero) REFERENCES cat_genero(id_genero)
            );
        """))

        # Tabla de Hechos de Ventas
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS ventas (
                id_registro {'INTEGER PRIMARY KEY AUTOINCREMENT' if is_sqlite else 'SERIAL PRIMARY KEY'},
                id_cliente INTEGER NOT NULL,
                fecha_compra DATE NOT NULL,
                monto_compra NUMERIC(12, 3),
                id_metodo_pago SMALLINT,
                id_navegador SMALLINT,
                tiempo NUMERIC(10, 2),
                boletin SMALLINT,
                vale SMALLINT,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_metodo_pago) REFERENCES cat_metodo_pago(id_metodo_pago),
                FOREIGN KEY (id_navegador) REFERENCES cat_navegador(id_navegador)
            );
        """))

        # Índices
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_clientes_genero ON clientes (id_genero);",
            "CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas (id_cliente);",
            "CREATE INDEX IF NOT EXISTS idx_ventas_fecha_compra ON ventas (fecha_compra);",
            "CREATE INDEX IF NOT EXISTS idx_ventas_metodo_pago ON ventas (id_metodo_pago);",
            "CREATE INDEX IF NOT EXISTS idx_ventas_navegador ON ventas (id_navegador);"
        ]
        for idx in indices:
            try:
                conn.execute(text(idx))
            except Exception:
                pass

        # Poblar catálogos con descripciones de negocio
        conn.execute(text("""
            INSERT INTO cat_genero (id_genero, descripcion) VALUES
            (0, 'Masculino'), (1, 'Femenino')
            ON CONFLICT (id_genero) DO NOTHING;
        """ if not is_sqlite else """
            INSERT OR IGNORE INTO cat_genero (id_genero, descripcion) VALUES
            (0, 'Masculino'), (1, 'Femenino');
        """))

        conn.execute(text("""
            INSERT INTO cat_metodo_pago (id_metodo_pago, descripcion) VALUES
            (0, 'Efectivo'), (1, 'Tarjeta de Crédito'), (2, 'Tarjeta de Débito')
            ON CONFLICT (id_metodo_pago) DO NOTHING;
        """ if not is_sqlite else """
            INSERT OR IGNORE INTO cat_metodo_pago (id_metodo_pago, descripcion) VALUES
            (0, 'Efectivo'), (1, 'Tarjeta de Crédito'), (2, 'Tarjeta de Débito');
        """))

        conn.execute(text("""
            INSERT INTO cat_navegador (id_navegador, descripcion) VALUES
            (0, 'Tienda Física'), (1, 'Navegador 1'), (2, 'Navegador 2'), (3, 'Navegador 3'), (4, 'Navegador 4')
            ON CONFLICT (id_navegador) DO NOTHING;
        """ if not is_sqlite else """
            INSERT OR IGNORE INTO cat_navegador (id_navegador, descripcion) VALUES
            (0, 'Tienda Física'), (1, 'Navegador 1'), (2, 'Navegador 2'), (3, 'Navegador 3'), (4, 'Navegador 4');
        """))

        # Vistas Analíticas
        if not is_sqlite:
            conn.execute(text("""
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
            """))

            conn.execute(text("""
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
            """))

    logger.info("Esquema relacional y catálogos creados exitosamente.")


def extract(file_path: str) -> pd.DataFrame:
    """
    Paso 1: EXTRACCIÓN
    Lee el archivo CSV de ventas identificando automáticamente delimitadores.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo fuente no fue encontrado en: {file_path}")

    logger.info(f"Iniciando extracción desde: {file_path}")
    separators = [';', ',', '\t', '|']
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    df = None
    for sep in separators:
        for enc in encodings:
            try:
                temp_df = pd.read_csv(file_path, sep=sep, encoding=enc)
                if temp_df.shape[1] >= 10:
                    df = temp_df
                    logger.info(f"Archivo leído con sep='{sep}', enc='{enc}'. Registros: {df.shape[0]}")
                    break
            except Exception:
                continue
        if df is not None:
            break

    if df is None or df.empty:
        raise ValueError(f"No se pudo parsear el archivo CSV: {file_path}")

    return df


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y estandariza los nombres de las columnas para coincidir con el esquema.
    """
    df = df.copy()
    cleaned_cols = {}
    for col in df.columns:
        norm = str(col).strip().lower().replace(' ', '_')
        if norm in EXPECTED_COLUMNS:
            cleaned_cols[col] = EXPECTED_COLUMNS[norm]
        else:
            cleaned_cols[col] = norm
    
    df.rename(columns=cleaned_cols, inplace=True)
    return df


def parse_dates_smart(series: pd.Series) -> pd.Series:
    """
    Parsea las fechas probando primero los formatos DD.MM.YY (ej: 02.02.21),
    DD/MM/YYYY, YYYY-MM-DD y finalmente fallback dayfirst=True.
    """
    parsed = pd.to_datetime(series, format='%d.%m.%y', errors='coerce')
    if parsed.notna().all():
        return parsed

    formats = ['%d.%m.%Y', '%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
    for fmt in formats:
        alt_parsed = pd.to_datetime(series, format=fmt, errors='coerce')
        if alt_parsed.notna().sum() > parsed.notna().sum():
            parsed = alt_parsed
            if parsed.notna().all():
                return parsed

    fallback = pd.to_datetime(series, dayfirst=True, errors='coerce')
    return parsed.fillna(fallback)


def transform(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Paso 2: TRANSFORMACIÓN Y SEPARACIÓN EN TABLAS NORMALIZADAS
    Retorna:
    - df_clientes (Dimensión Clientes)
    - df_ventas (Hechos de Transacciones de Ventas)
    """
    logger.info("Iniciando fase de Transformación y Limpieza...")
    total_inicial = len(df_raw)
    
    df = normalize_column_names(df_raw)

    # 1. Duplicados exactos
    dups = df.duplicated().sum()
    if dups > 0:
        logger.info(f"Eliminando {dups} filas duplicadas...")
        df = df.drop_duplicates().copy()

    # 2. Fechas
    if 'fecha_compra' in df.columns:
        parsed_dates = parse_dates_smart(df['fecha_compra'])
        df['fecha_compra'] = parsed_dates.dt.date

    # 3. Limpieza Numérica
    numeric_cols = ['venta_total', 'monto_compra', 'tiempo']
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    int_cols = ['id_cliente', 'edad', 'n_compras', 'id_genero', 'id_metodo_pago', 'id_navegador', 'boletin', 'vale']
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Validar rangos de catálogos
    if 'id_genero' in df.columns:
        df.loc[~df['id_genero'].isin([0, 1]), 'id_genero'] = np.nan
    if 'id_metodo_pago' in df.columns:
        df.loc[~df['id_metodo_pago'].isin([0, 1, 2]), 'id_metodo_pago'] = np.nan
    if 'id_navegador' in df.columns:
        df.loc[~df['id_navegador'].isin([0, 1, 2, 3, 4]), 'id_navegador'] = np.nan

    # Eliminar registros sin id_cliente válido
    df = df.dropna(subset=['id_cliente']).copy()
    df['id_cliente'] = df['id_cliente'].astype(int)

    # --- SEPARAR TABLA CLIENTES ---
    cols_cliente = ['id_cliente', 'edad', 'id_genero', 'venta_total', 'n_compras']
    df_clientes = df[cols_cliente].drop_duplicates(subset=['id_cliente']).copy()

    # --- SEPARAR TABLA VENTAS ---
    cols_ventas = [
        'id_cliente', 'fecha_compra', 'monto_compra',
        'id_metodo_pago', 'id_navegador', 'tiempo', 'boletin', 'vale'
    ]
    df_ventas = df[cols_ventas].copy()

    logger.info(f"Transformación completada: {len(df_clientes)} clientes únicos, {len(df_ventas)} transacciones.")
    return df_clientes, df_ventas


def load(df_clientes: pd.DataFrame, df_ventas: pd.DataFrame, engine, if_exists: str = "replace"):
    """
    Paso 3: CARGA HACIA AWS RDS
    Carga ordenada respetando la integridad referencial (Clientes primero, luego Ventas).
    """
    logger.info("Iniciando carga estructurada a la base de datos relacional...")
    
    try:
        # Recrear esquema limpio si el modo es 'replace'
        init_database_schema(engine, drop_existing=(if_exists == "replace"))

        # 1. Cargar Clientes
        logger.info(f"Cargando {len(df_clientes)} registros en la tabla 'clientes'...")
        df_clientes.to_sql(
            name="clientes",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi"
        )

        # 2. Cargar Ventas
        logger.info(f"Cargando {len(df_ventas)} transacciones en la tabla 'ventas'...")
        df_ventas.to_sql(
            name="ventas",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi"
        )

        # Verificación y estadísticas
        with engine.connect() as conn:
            tot_clientes = conn.execute(text("SELECT COUNT(*) FROM clientes;")).scalar()
            tot_ventas = conn.execute(text("SELECT COUNT(*) FROM ventas;")).scalar()
            tot_facturado = conn.execute(text("SELECT SUM(monto_compra) FROM ventas;")).scalar() or 0.0

        logger.info("¡Carga relacional finalizada con total éxito!")
        logger.info(f"- Total Clientes en 'clientes': {tot_clientes}")
        logger.info(f"- Total Ventas en 'ventas': {tot_ventas}")
        logger.info(f"- Monto Total Facturado: ${float(tot_facturado):,.2f}")

    except Exception as e:
        logger.error(f"Error durante la carga a la base de datos: {e}")
        raise


def find_csv_file(specified_path: Optional[str] = None) -> str:
    if specified_path and os.path.exists(specified_path):
        return specified_path

    candidates = [
        str(BASE_DIR / "data" / "Venta_online_c.csv"),
        str(BASE_DIR / "Venta_online_c.csv"),
        "data/Venta_online_c.csv",
        "../data/Venta_online_c.csv",
        "Venta_online_c.csv",
        "../Venta_online_c.csv",
        "ventas_2021.csv"
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    for search_dir in [str(BASE_DIR / "data"), str(BASE_DIR), ".", ".."]:
        if os.path.exists(search_dir):
            for f in os.listdir(search_dir):
                if f.endswith(".csv"):
                    return os.path.join(search_dir, f)

    return str(BASE_DIR / "data" / "Venta_online_c.csv")


def run_etl(file_path: Optional[str] = None, db_url: Optional[str] = None, mode: str = "replace"):
    logger.info("==================================================")
    logger.info("Iniciando ETL Normalizado / Estrella - Práctica 1")
    logger.info("==================================================")
    
    csv_file = find_csv_file(file_path)
    engine = get_db_engine(db_url)
    df_raw = extract(csv_file)
    df_clientes, df_ventas = transform(df_raw)
    load(df_clientes, df_ventas, engine, if_exists=mode)

    logger.info("==================================================")
    logger.info("Proceso ETL Relacional finalizado exitosamente.")
    logger.info("==================================================")


def main():
    parser = argparse.ArgumentParser(description="ETL Pipeline Relacional Normalizado para AWS RDS.")
    parser.add_argument("--file", "-f", type=str, default=None, help="Ruta al archivo CSV")
    parser.add_argument("--db-url", "-d", type=str, default=None, help="Cadena de conexión a base de datos")
    parser.add_argument("--mode", "-m", type=str, choices=["append", "replace"], default="replace")

    args = parser.parse_args()
    run_etl(file_path=args.file, db_url=args.db_url, mode=args.mode)


if __name__ == "__main__":
    main()
