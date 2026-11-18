"""TP N.º 4 — Sistemas Operativos II (2026) | Discos y sellos discográficos."""

import logging
import os

import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# Apache envía X-Forwarded-Prefix; sin proxy también funciona en /.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=0, x_proto=0, x_host=0, x_port=0, x_prefix=1)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def conectar_db():
    """Conexión PostgreSQL configurada exclusivamente mediante variables de entorno."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "sellos_discos"),
        user=os.getenv("DB_USER", "app_discos"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=4,
        autocommit=True,
        row_factory=dict_row,
    )


@app.get("/")
def inicio():
    discos = []
    db_disponible = True
    try:
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                # El listado es proporcionado por la función almacenada.
                cursor.execute("SELECT * FROM public.listar_discos()")
                discos = cursor.fetchall()
    except (psycopg.Error, OSError, KeyError, ValueError):
        app.logger.exception("No se pudo obtener el catálogo de discos")
        db_disponible = False

    return render_template(
        "index.html", discos=discos, db_disponible=db_disponible
    )


@app.get("/api/discos/<int:disco_id>")
def detalle_disco(disco_id):
    if disco_id <= 0:
        return jsonify(error="Identificador inválido."), 400

    try:
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                # Parámetro tipado: ninguna consulta directa a las tablas.
                cursor.execute(
                    "SELECT * FROM public.obtener_disco(%s::integer)",
                    (disco_id,),
                )
                disco = cursor.fetchone()
    except (psycopg.Error, OSError, KeyError, ValueError):
        app.logger.exception("No se pudo consultar el disco %s", disco_id)
        return jsonify(error="No se pudo consultar PostgreSQL."), 503

    if disco is None:
        return jsonify(error="No se encontró el disco seleccionado."), 404

    return jsonify(anio=disco["anio"], sello=disco["sello"])


@app.get("/health")
def salud():
    """Estado HTTP de Flask; no es un chequeo de PostgreSQL."""
    return jsonify(servicio="sellos-discos", estado="ok")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
