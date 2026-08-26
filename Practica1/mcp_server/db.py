import os
import pathlib

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv(pathlib.Path(__file__).resolve().parents[1] / ".env")

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError(
                "Falta DATABASE_URL en el archivo .env "
            )
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def consultar(sql: str, **params) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params)
