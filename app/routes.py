import re
from datetime import date, timedelta
from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import app
from .base_datos import conectar, ErrorIntegridad

tipos = ["Reciclaje", "Ahorro de agua", "Transporte", "Energía"]


FACTOR_CO2_APROX = 0.435
META_SEMANAL = 5
UNIDADES = {
    "Reciclaje": "kg",
    "Ahorro de agua": "litros",
    "Transporte": "kg CO₂",
    "Energía": "kWh",
}
PERIODOS = {
    "7": "Últimos 7 días",
    "mes": "Este mes",
    "todo": "Todo",
}
def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("sesion"))
        return vista(*args, **kwargs)
    return envoltura

def acciones_del_usuario():
    with conectar() as conexion:
        return conexion.execute(
            "SELECT * FROM acciones WHERE usuario_id = ? ORDER BY fecha DESC, id DESC",
            (session["usuario_id"],),
        ).fetchall()
def buscar_accion(id):
    with conectar() as conexion:
        return conexion.execute(
            "SELECT * FROM acciones WHERE id = ? AND usuario_id = ?",
            (id, session["usuario_id"]),
        ).fetchone()
def leer_formulario():
    return (
        request.form.get("tipo", "").strip(),
        request.form.get("descripcion", "").strip(),
        request.form.get("fecha", "").strip(),
        request.form.get("impacto", "").strip(),
    )
def formulario_valido(tipo, descripcion, fecha, impacto):
    return (
        tipo in tipos
        and len(descripcion) >= 5
        and fecha != ""
        and re.search(r"\d", impacto) is not None
    )
def numero_de(texto):
    encontrado = re.search(r"\d+(?:[.,]\d+)?", texto)
    return float(encontrado.group().replace(",", ".")) if encontrado else 0
def formatear(numero):
    return int(numero) if numero == int(numero) else round(numero, 1)
def texto_plano(texto):
    return texto.lower().replace("₂", "2")
def calcular_co2(acciones):
    transporte = sum(numero_de(a["impacto"]) for a in acciones if "co2" in texto_plano(a["impacto"]))
    energia = sum(numero_de(a["impacto"]) * FACTOR_CO2_APROX for a in acciones if "kwh" in texto_plano(a["impacto"]))
    return transporte + energia
def desde_periodo(periodo, hoy):
    if periodo == "7":
        return hoy - timedelta(days=6)
    if periodo == "mes":
        return hoy.replace(day=1)
    return None
def calcular_resumen(acciones):
    litros = sum(numero_de(a["impacto"]) for a in acciones if "litro" in texto_plano(a["impacto"]))
    reciclado = sum(numero_de(a["impacto"]) for a in acciones if a["tipo"] == "Reciclaje")
    return {
        "total": len(acciones),
        "litros": formatear(litros),
        "reciclado": formatear(reciclado),
        "co2": formatear(calcular_co2(acciones)),
    }
@app.route("/", methods=["GET", "POST"])
def sesion():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")
        with conectar() as conexion:
            fila = conexion.execute(
                "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
            ).fetchone()
        if fila and check_password_hash(fila["contrasena"], contrasena):
            session["usuario_id"] = fila["id"]
            session["usuario"] = fila["usuario"]
            return redirect(url_for("principal"))
        flash("Usuario o contraseña incorrectos.", "error")
        return redirect(url_for("sesion"))
    return render_template("sesion.html")
@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")
        if len(usuario) < 3 or len(contrasena) < 6:
            flash("Revisa los datos del formulario.", "error")
            return redirect(url_for("registrar"))
        try:
            with conectar() as conexion:
                conexion.execute(
                    "INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)",
                    (usuario, generate_password_hash(contrasena)),
                )
        except ErrorIntegridad:
            flash("Ese usuario ya existe. Elige otro.", "error")
            return redirect(url_for("registrar"))
        flash("Cuenta creada. Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("sesion"))
    return render_template("registrar.html")
@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("sesion"))
@app.route("/principal")
@login_requerido
def principal():
    acciones = acciones_del_usuario()
    return render_template("principal.html", acciones=acciones, resumen=calcular_resumen(acciones))
@app.route("/nueva", methods=["GET", "POST"])
@login_requerido
def nueva():
    if request.method == "POST":
        tipo, descripcion, fecha, impacto = leer_formulario()
        if not formulario_valido(tipo, descripcion, fecha, impacto):
            flash("Revisa los datos del formulario.", "error")
            return redirect(url_for("nueva"))
        with conectar() as conexion:
            conexion.execute(
                "INSERT INTO acciones (usuario_id, fecha, tipo, descripcion, impacto) VALUES (?, ?, ?, ?, ?)",
                (session["usuario_id"], fecha, tipo, descripcion, impacto),
            )
        flash("Acción guardada correctamente.", "exito")
        return redirect(url_for("principal"))
    return render_template("formulario.html", accion=None, tipos=tipos)
@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_requerido
def editar(id):
    accion = buscar_accion(id)
    if accion is None:
        return redirect(url_for("principal"))
    if request.method == "POST":
        tipo, descripcion, fecha, impacto = leer_formulario()
        if not formulario_valido(tipo, descripcion, fecha, impacto):
            flash("Revisa los datos del formulario.", "error")
            return redirect(url_for("editar", id=id))
        with conectar() as conexion:
            conexion.execute(
                "UPDATE acciones SET tipo = ?, descripcion = ?, fecha = ?, impacto = ? WHERE id = ? AND usuario_id = ?",
                (tipo, descripcion, fecha, impacto, id, session["usuario_id"]),
            )
        flash("Acción actualizada.", "exito")
        return redirect(url_for("principal"))
    return render_template("formulario.html", accion=accion, tipos=tipos)
@app.route("/eliminar/<int:id>", methods=["POST"])
@login_requerido
def eliminar(id):
    with conectar() as conexion:
        conexion.execute(
            "DELETE FROM acciones WHERE id = ? AND usuario_id = ?",
            (id, session["usuario_id"]),
        )
    flash("Acción eliminada.", "exito")
    return redirect(url_for("principal"))
@app.route("/detalle/<int:id>")
@login_requerido
def detalle(id):
    accion = buscar_accion(id)
    if accion is None:
        return redirect(url_for("principal"))
    return render_template("detalle.html", accion=accion)
@app.route("/estadisticas")
@login_requerido
def estadisticas():
    periodo = request.args.get("periodo", "todo")
    if periodo not in PERIODOS:
        periodo = "todo"
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)
    desde = desde_periodo(periodo, hoy)
    with conectar() as conexion:
        hechas = conexion.execute(
            "SELECT COUNT(*) AS total FROM acciones WHERE usuario_id = ? AND fecha BETWEEN ? AND ?",
            (session["usuario_id"], lunes.isoformat(), domingo.isoformat()),
        ).fetchone()["total"]
        if desde:
            acciones = conexion.execute(
                "SELECT * FROM acciones WHERE usuario_id = ? AND fecha BETWEEN ? AND ?",
                (session["usuario_id"], desde.isoformat(), hoy.isoformat()),
            ).fetchall()
        else:
            acciones = conexion.execute(
                "SELECT * FROM acciones WHERE usuario_id = ?",
                (session["usuario_id"],),
            ).fetchall()
    por_tipo = []
    for t in tipos:
        de_este_tipo = [a for a in acciones if a["tipo"] == t]
        total_tipo = sum(numero_de(a["impacto"]) for a in de_este_tipo)
        por_tipo.append({
            "tipo": t,
            "cantidad": len(de_este_tipo),
            "total": formatear(total_tipo),
            "unidad": UNIDADES[t],
        })
    meta = {
        "hechas": hechas,
        "objetivo": META_SEMANAL,
        "porcentaje": min(100, round(hechas * 100 / META_SEMANAL)),
        "faltan": max(0, META_SEMANAL - hechas),
        "desde": lunes.strftime("%d/%m"),
        "hasta": domingo.strftime("%d/%m"),
    }
    return render_template(
        "estadisticas.html",
        meta=meta,
        por_tipo=por_tipo,
        total=len(acciones),
        co2=formatear(calcular_co2(acciones)),
        periodos=PERIODOS,
        periodo=periodo,
    )
