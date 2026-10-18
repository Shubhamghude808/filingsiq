from contextlib import contextmanager

import psycopg
from pgvector.psycopg import register_vector

from filingsiq.config import settings


@contextmanager
def get_conn():
    with psycopg.connect(settings.database_url) as conn:
        register_vector(conn)
        yield conn
