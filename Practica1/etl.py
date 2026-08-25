"""
ETL Pipeline - Práctica 1: Sistemas Organizacionales y Gerenciales 2 (2S2026)
-----------------------------------------------------------------------------
Este script realiza el proceso de Extracción, Transformación y Carga (ETL)
de los datos de ventas para el análisis exploratorio y posterior consumo
por la base de datos en la nube y el agente de IA / MCP Server.

Estructura requerida por el enunciado:
- Id_cliente: Identificador único o del cliente (INT)
- Edad: Edad del cliente (INT)
- Genero: 0 = Masculino, 1 = Femenino (SMALLINT)
- Venta_total: Monto total acumulado o de la venta (DECIMAL / NUMERIC)
- N_Compras: Número de compras realizadas (INT)
- FechaCompra: Fecha en que se realizó la compra (DATE)
- MontoCompra: Monto de la transacción (DECIMAL / NUMERIC)
- MetodoPago: 0 = Efectivo, 1 = Tarjeta de Crédito, 2 = Tarjeta de Débito (SMALLINT)
- Tiempo: Tiempo transcurrido / navegación (FLOAT / NUMERIC)
- Navegador: 0 = Tienda Física, 1 = Navegador 1, 2 = Navegador 2, 3 = Navegador 3, 4 = Navegador 4 (SMALLINT)
- Boletín: 0 = No, 1 = Sí (SMALLINT / BOOLEAN)
- Vale: 0 = No, 1 = Sí (SMALLINT / BOOLEAN)
"""

import os
import sys
import argparse
import logging
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, Table, Column, Integer, SmallInteger, Numeric, Date, MetaData, inspect
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ETL_Practica1")

# Mapeo y estandarización de columnas esperadas
EXPECTED_COLUMNS = {
    'id_cliente': 'id_cliente',
    'edad': 'edad',
    'genero': 'genero',
    'venta_total': 'venta_total',
    'n_compras': 'n_compras',
    'fechacompra': 'fecha_compra',
    'fecha_compra': 'fecha_compra',
    'montocompra': 'monto_compra',
    'monto_compra': 'monto_compra',
    'metodopago': 'metodo_pago',
    'metodo_pago': 'metodo_pago',
    'tiempo': 'tiempo',
    'navegador': 'navegador',
    'boletin': 'boletin',
    'boletín': 'boletin',
    'vale': 'vale'
}

TABLE_NAME = "ventas"


def get_db_engine(db_url: Optional[str] = None):
    """
    Crea y retorna el motor de SQLAlchemy conectado a la base de datos.
    Toma la URL de los parámetros, del archivo .env (DATABASE_URL) o usa SQLite por defecto.
    """
    connection_string = db_url or os.getenv("DATABASE_URL")
    if not connection_string:
        default_sqlite = "sqlite:///practica1_local.db"
        logger.warning(f"No se proporcionó DATABASE_URL en .env ni como argumento. Usando SQLite local para pruebas: {default_sqlite}")
        connection_string = default_sqlite
    
    # Manejo de compatibilidad con PostgreSQL en caso de que empiece con postgres://
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


def create_schema(engine):
    """
    Crea la tabla en la base de datos relacional si no existe, con los tipos de datos requeridos por el enunciado.
    """
    metadata = MetaData()

    ventas_table = Table(
        TABLE_NAME,
        metadata,
        Column('id_registro', Integer, primary_key=True, autoincrement=True),
        Column('id_cliente', Integer, nullable=False, index=True),
        Column('edad', Integer, nullable=True),
        Column('genero', SmallInteger, nullable=True),       # 0: Masculino, 1: Femenino
        Column('venta_total', Numeric(12, 2), nullable=True),
        Column('n_compras', Integer, nullable=True),
        Column('fecha_compra', Date, nullable=True, index=True),
        Column('monto_compra', Numeric(12, 3), nullable=True),
        Column('metodo_pago', SmallInteger, nullable=True),  # 0: Efectivo, 1: TDC, 2: TDD
        Column('tiempo', Numeric(10, 2), nullable=True),
        Column('navegador', SmallInteger, nullable=True),    # 0: Física, 1..4: Navegadores
        Column('boletin', SmallInteger, nullable=True),      # 0: No, 1: Sí
        Column('vale', SmallInteger, nullable=True)          # 0: No, 1: Sí
    )

    metadata.create_all(engine)
    logger.info(f"Esquema verificado/creado exitosamente para la tabla '{TABLE_NAME}'.")


def extract(file_path: str) -> pd.DataFrame:
    """
    Paso 1: EXTRACCIÓN
    Lee el archivo CSV de ventas identificando automáticamente delimitadores y codificaciones.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo fuente no fue encontrado en: {file_path}")

    logger.info(f"Iniciando extracción desde: {file_path}")

    # Probar delimitadores comunes (; suele ser el estándar en datasets en español / excel)
    separators = [';', ',', '\t', '|']
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    df = None
    for sep in separators:
        for enc in encodings:
            try:
                temp_df = pd.read_csv(file_path, sep=sep, encoding=enc)
                # Validar que tenga más de 1 columna y que tenga las columnas esperadas
                if temp_df.shape[1] >= 10:
                    df = temp_df
                    logger.info(f"Archivo leído correctamente con separador='{sep}' y codificación='{enc}'. Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
                    break
            except Exception:
                continue
        if df is not None:
            break

    if df is None or df.empty:
        raise ValueError(f"No se pudo parsear el archivo CSV o está vacío: {file_path}")

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
    # Intentar formato específico del dataset: %d.%m.%y
    parsed = pd.to_datetime(series, format='%d.%m.%y', errors='coerce')
    if parsed.notna().all():
        return parsed

    # Fallback probando otros formatos comunes
    formats = ['%d.%m.%Y', '%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
    for fmt in formats:
        alt_parsed = pd.to_datetime(series, format=fmt, errors='coerce')
        if alt_parsed.notna().sum() > parsed.notna().sum():
            parsed = alt_parsed
            if parsed.notna().all():
                return parsed

    # Fallback general
    fallback = pd.to_datetime(series, dayfirst=True, errors='coerce')
    return parsed.fillna(fallback)


def transform(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Paso 2: TRANSFORMACIÓN Y LIMPIEZA
    - Normalización de nombres de columnas
    - Verificación y eliminación de registros duplicados
    - Manejo de valores faltantes
    - Conversión y validación de tipos de datos:
      * id_cliente: Integer
      * edad: Integer
      * genero: 0 o 1
      * venta_total, monto_compra: Decimales / Numeric
      * n_compras: Integer
      * fecha_compra: Date (YYYY-MM-DD)
      * metodo_pago: 0, 1 o 2
      * tiempo: Numérico
      * navegador: 0 a 4
      * boletin, vale: 0 o 1
    """
    logger.info("Iniciando fase de Transformación y Limpieza...")
    total_inicial = len(df_raw)
    
    # 1. Normalizar nombres de columnas
    df = normalize_column_names(df_raw)

    # 2. Manejo de duplicados
    duplicados_completos = df.duplicated().sum()
    if duplicados_completos > 0:
        logger.info(f"Se encontraron {duplicados_completos} filas duplicadas exactas. Eliminando duplicados...")
        df = df.drop_duplicates().copy()

    # 3. Conversión y formateo de FechaCompra
    if 'fecha_compra' in df.columns:
        parsed_dates = parse_dates_smart(df['fecha_compra'])
        fechas_nulas = parsed_dates.isna().sum()
        if fechas_nulas > 0:
            logger.warning(f"Se encontraron {fechas_nulas} registros con fecha inválida/nula.")
        df['fecha_compra'] = parsed_dates.dt.date

    # 4. Limpieza de variables numéricas y monetarias
    numeric_cols = ['venta_total', 'monto_compra', 'tiempo']
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 5. Limpieza de variables enteras
    int_cols = ['id_cliente', 'edad', 'n_compras', 'genero', 'metodo_pago', 'navegador', 'boletin', 'vale']
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 6. Validación de rangos y valores categóricos según el enunciado
    # Genero: 0 (Masculino), 1 (Femenino)
    if 'genero' in df.columns:
        df.loc[~df['genero'].isin([0, 1]), 'genero'] = np.nan

    # MetodoPago: 0 (Efectivo), 1 (Tarjeta de Crédito), 2 (Tarjeta de Débito)
    if 'metodo_pago' in df.columns:
        df.loc[~df['metodo_pago'].isin([0, 1, 2]), 'metodo_pago'] = np.nan

    # Navegador: 0 (Tienda Física), 1..4 (Navegadores)
    if 'navegador' in df.columns:
        df.loc[~df['navegador'].isin([0, 1, 2, 3, 4]), 'navegador'] = np.nan

    # Boletin & Vale: 0 (No), 1 (Sí)
    for flag_col in ['boletin', 'vale']:
        if flag_col in df.columns:
            df.loc[~df[flag_col].isin([0, 1]), flag_col] = np.nan

    # 7. Resumen de nulos por columna
    nulls_summary = df.isna().sum()
    nulos_detectados = nulls_summary[nulls_summary > 0]
    if not nulos_detectados.empty:
        logger.info("Resumen de valores nulos tras la transformación:\n" + str(nulos_detectados))
    else:
        logger.info("No se encontraron valores nulos en el dataset.")

    # 8. Eliminar filas sin id_cliente si hubiese alguna
    if 'id_cliente' in df.columns:
        invalid_ids = df['id_cliente'].isna().sum()
        if invalid_ids > 0:
            logger.warning(f"Eliminando {invalid_ids} registros sin id_cliente válido.")
            df = df.dropna(subset=['id_cliente']).copy()

    # Seleccionar las columnas en el orden del modelo relacional
    cols_to_keep = [c for c in [
        'id_cliente', 'edad', 'genero', 'venta_total', 'n_compras',
        'fecha_compra', 'monto_compra', 'metodo_pago', 'tiempo',
        'navegador', 'boletin', 'vale'
    ] if c in df.columns]

    df_final = df[cols_to_keep].copy()

    logger.info(f"Transformación finalizada exitosamente. Filas procesadas: {len(df_final)}/{total_inicial}")
    return df_final


def load(df: pd.DataFrame, engine, if_exists: str = "append", chunksize: int = 1000):
    """
    Paso 3: CARGA
    Inserta los datos limpios en la tabla de la base de datos SQL en la nube.
    """
    logger.info(f"Iniciando carga a la tabla '{TABLE_NAME}' en la base de datos...")
    
    if df.empty:
        logger.warning("El DataFrame a cargar está vacío. Carga omitida.")
        return

    try:
        # Asegurar que el esquema existe
        create_schema(engine)

        # Si se desea reiniciar la tabla antes de cargar
        if if_exists == "replace":
            with engine.begin() as conn:
                conn.execute(text(f"DELETE FROM {TABLE_NAME}"))
            logger.info(f"Tabla '{TABLE_NAME}' reiniciada/limpiada antes de la carga.")

        # Carga por lotes a la base de datos
        df.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi"
        )

        with engine.connect() as conn:
            total_records = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()
            # Muestra de verificación
            sample_query = conn.execute(text(f"SELECT MIN(fecha_compra), MAX(fecha_compra), SUM(venta_total) FROM {TABLE_NAME}")).fetchone()

        logger.info(f"¡Carga completada exitosamente!")
        logger.info(f"- Registros totales en '{TABLE_NAME}': {total_records}")
        if sample_query:
            logger.info(f"- Rango de fechas: {sample_query[0]} a {sample_query[1]}")
            logger.info(f"- Suma total de ventas: ${sample_query[2]:,.2f}")
    except Exception as e:
        logger.error(f"Error durante la carga a la base de datos: {e}")
        raise


def find_csv_file(specified_path: Optional[str] = None) -> str:
    """
    Localiza el archivo CSV buscando en las rutas más probables del proyecto.
    """
    if specified_path and os.path.exists(specified_path):
        return specified_path

    # Lista de candidatos por prioridad
    candidates = [
        "Venta_online_c.csv",
        "../Venta_online_c.csv",
        "ventas_2021.csv",
        "../ventas_2021.csv",
        "data.csv",
        "../data.csv"
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    # Si no se encuentra ninguno de los conocidos, buscar cualquier .csv en . o ..
    for search_dir in [".", ".."]:
        if os.path.exists(search_dir):
            for f in os.listdir(search_dir):
                if f.endswith(".csv"):
                    return os.path.join(search_dir, f)

    return specified_path or "Venta_online_c.csv"


def run_etl(file_path: Optional[str] = None, db_url: Optional[str] = None, mode: str = "replace"):
    """
    Ejecuta el flujo completo de ETL (Extract, Transform, Load).
    """
    logger.info("==========================================")
    logger.info("Iniciando Pipeline ETL - Práctica 1 (SOG2)")
    logger.info("==========================================")
    
    csv_file = find_csv_file(file_path)
    engine = get_db_engine(db_url)
    df_raw = extract(csv_file)
    df_clean = transform(df_raw)
    load(df_clean, engine, if_exists=mode)

    logger.info("==========================================")
    logger.info("Proceso ETL finalizado con éxito.")
    logger.info("==========================================")


def main():
    parser = argparse.ArgumentParser(
        description="ETL Pipeline para carga de datos de Ventas 2021 en BD SQL en la nube."
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Ruta al archivo CSV de ventas (por defecto busca Venta_online_c.csv)"
    )
    parser.add_argument(
        "--db-url", "-d",
        type=str,
        default=None,
        help="Cadena de conexión SQLAlchemy / PostgreSQL / MySQL (o usar variable DATABASE_URL en .env)"
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["append", "replace"],
        default="replace",
        help="Modo de carga: 'replace' para limpiar e insertar de nuevo, 'append' para agregar."
    )

    args = parser.parse_args()
    run_etl(file_path=args.file, db_url=args.db_url, mode=args.mode)


if __name__ == "__main__":
    main()
