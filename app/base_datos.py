import os
import sqlite3

CARPETA = os.path.dirname(__file__)
URL_BD = os.environ.get("DATABASE_URL")
USA_POSTGRES = bool(URL_BD)

if USA_POSTGRES:
    import psycopg
    from psycopg.rows import dict_row
    ErrorIntegridad = psycopg.IntegrityError
    RUTA_ESQUEMA = os.path.join(CARPETA, "schema_postgres.sql")
else:
    ErrorIntegridad = sqlite3.IntegrityError
    RUTA_ESQUEMA = os.path.join(CARPETA, "schema.sql")

RUTA_BD = os.path.join(CARPETA, "ecoreto.db")


class Conexion:
    def __init__(self, conexion):
        self.conexion = conexion

    def execute(self, consulta, parametros=()):
        if USA_POSTGRES:
            consulta = consulta.replace("?", "%s")
        return self.conexion.execute(consulta, parametros)

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, rastro):
        if tipo is None:
            self.conexion.commit()
        else:
            self.conexion.rollback()
        self.conexion.close()
        return False


def conectar():
    if USA_POSTGRES:
        return Conexion(psycopg.connect(URL_BD, row_factory=dict_row))
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return Conexion(conexion)


def crear_tablas():
    with open(RUTA_ESQUEMA, encoding="utf-8") as archivo:
        sentencias = [s.strip() for s in archivo.read().split(";") if s.strip()]
    with conectar() as conexion:
        for sentencia in sentencias:
            conexion.execute(sentencia)