import os
from flask import Flask
from .base_datos import crear_tablas

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo")

crear_tablas()
from . import routes