import os
import random
import webbrowser
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

try:
    import qrcode
except ImportError:
    qrcode = None

app = Flask(__name__)
app.secret_key = "aquacajay-dev-secret"  # solo para prototipo

WHATSAPP_NUMERO = "51906568414"  # número de contacto de la junta de agua

# Enlace público de la app. Mientras corre solo en tu PC, usa localhost;
# cuando la publiques en internet (Render, PythonAnywhere, etc.), cambia
# este valor por esa URL para que el link funcione para cualquier vecino.
APP_URL = "http://192.168.170.153:5000"

# ---------------------------------------------------------------------------
# Datos simulados (en un proyecto real vendrían de una base de datos)
# ---------------------------------------------------------------------------

ZONAS = [
    {"nombre": "Cajay Centro", "estado": "normal", "nivel": 86, "actualizado": "hace 12 min"},
    {"nombre": "Barrio Alto", "estado": "corte", "nivel": 10, "actualizado": "hace 40 min"},
    {"nombre": "La Ribera", "estado": "bajo", "nivel": 38, "actualizado": "hace 25 min"},
    {"nombre": "San Isidro Rural", "estado": "normal", "nivel": 74, "actualizado": "hace 1 h"},
]

ESTADOS = {
    "normal": {"etiqueta": "Suministro normal", "clase": "pill-normal"},
    "corte": {"etiqueta": "Corte programado", "clase": "pill-corte"},
    "bajo": {"etiqueta": "Presión baja", "clase": "pill-bajo"},
}

AVISOS = [
    {
        "titulo": "Corte programado en Barrio Alto",
        "fecha": "10 de julio, 2026",
        "tipo": "urgente",
        "cuerpo": "Se realizarán trabajos de mantenimiento en la línea principal. El servicio se restablecerá "
                   "el mismo día antes de las 6:00 p.m.",
    },
    {
        "titulo": "Nueva cisterna de reserva en La Ribera",
        "fecha": "6 de julio, 2026",
        "tipo": "informativo",
        "cuerpo": "La comunidad ya cuenta con una cisterna adicional de 10,000 litros para reforzar el "
                   "abastecimiento en horas de mayor demanda.",
    },
    {
        "titulo": "Recomendaciones para el almacenamiento seguro de agua",
        "fecha": "2 de julio, 2026",
        "tipo": "aviso",
        "cuerpo": "Recuerda mantener los tanques y recipientes tapados y limpiarlos cada 15 días para evitar "
                   "contaminación.",
    },
    {
        "titulo": "Asamblea comunitaria del agua",
        "fecha": "28 de junio, 2026",
        "tipo": "informativo",
        "cuerpo": "Los invitamos a la reunión mensual de la junta de agua para revisar el estado de las obras "
                   "y resolver dudas de los vecinos.",
    },
]

REPORTES_PERFIL = [
    {"codigo": "AC-1042", "tipo": "Fuga visible", "zona": "Cajay Centro", "fecha": "8 jul 2026", "estado": "Resuelto"},
    {"codigo": "AC-1058", "tipo": "Baja presión", "zona": "La Ribera", "fecha": "10 jul 2026", "estado": "En revisión"},
]

TIPOS_INCIDENCIA = ["Falta de agua", "Fuga visible", "Baja presión", "Agua contaminada", "Otro"]


def usuario_actual():
    return session.get("usuario")


@app.context_processor
def inject_globals():
    return {
        "usuario": usuario_actual(),
        "anio": datetime.now().year,
        "whatsapp_numero": WHATSAPP_NUMERO,
        "zonas_nombres": [z["nombre"] for z in ZONAS],
        "app_url": APP_URL,
    }


# ---------------------------------------------------------------------------
# Páginas públicas
# ---------------------------------------------------------------------------

@app.route("/")
def splash():
    return render_template("splash.html")


@app.route("/inicio")
def index():
    return render_template("index.html", zonas=ZONAS[:3], estados=ESTADOS)


@app.route("/avisos")
def avisos():
    return render_template("avisos.html", avisos=AVISOS)


@app.route("/api/notificaciones")
def api_notificaciones():
    """Simula una notificación en vivo sobre el estado de una zona aleatoria."""
    zona = random.choice(ZONAS)
    info = ESTADOS[zona["estado"]]
    mensajes = {
        "normal": f"{zona['nombre']} está funcionando con normalidad ({zona['nivel']}% de nivel).",
        "corte": f"{zona['nombre']} sigue con el corte programado. Te avisaremos al restablecerse.",
        "bajo": f"{zona['nombre']} reporta presión baja. La cuadrilla ya fue notificada.",
    }
    notificacion = {
        "zona": zona["nombre"],
        "estado": zona["estado"],
        "etiqueta": info["etiqueta"],
        "mensaje": mensajes[zona["estado"]],
        "hora": datetime.now().strftime("%H:%M"),
    }
    return jsonify(notificacion)


@app.route("/suministro")
def suministro():
    return render_template("suministro.html", zonas=ZONAS, estados=ESTADOS)


@app.route("/reportar", methods=["GET", "POST"])
def reportar():
    if request.method == "POST":
        codigo = f"AC-{random.randint(1000, 9999)}"
        flash(f"Reporte enviado. Tu código de seguimiento es {codigo}.", "exito")
        return redirect(url_for("reportar"))
    return render_template("reportar.html", tipos=TIPOS_INCIDENCIA, zonas=ZONAS)


# ---------------------------------------------------------------------------
# Cuenta
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        if correo:
            session["usuario"] = {"nombre": correo.split("@")[0].capitalize(), "correo": correo}
            flash("Bienvenido de nuevo.", "exito")
            return redirect(url_for("index"))
        flash("Ingresa un correo válido.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        zona = request.form.get("zona", "")
        if nombre and correo:
            session["usuario"] = {"nombre": nombre, "correo": correo, "zona": zona}
            flash("Cuenta creada correctamente.", "exito")
            return redirect(url_for("index"))
        flash("Completa tu nombre y correo para continuar.", "error")
    return render_template("register.html", zonas=ZONAS)


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Cerraste sesión correctamente.", "exito")
    return redirect(url_for("index"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        flash("Si el correo existe en nuestro sistema, te enviaremos instrucciones para continuar.", "exito")
        return redirect(url_for("forgot_password"))
    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        nueva = request.form.get("password", "")
        confirmar = request.form.get("password_confirm", "")
        if nueva and nueva == confirmar:
            flash("Tu contraseña se actualizó correctamente.", "exito")
            return redirect(url_for("login"))
        flash("Las contraseñas no coinciden.", "error")
    return render_template("reset_password.html")


@app.route("/mi-perfil")
def mi_perfil():
    if not usuario_actual():
        flash("Inicia sesión para ver tu perfil.", "error")
        return redirect(url_for("login"))
    return render_template("perfil.html", reportes=REPORTES_PERFIL)


def generar_qr():
    """Genera un QR (imagen + versión en la terminal) que apunta a APP_URL,
    para que cualquiera pueda escanearlo y abrir la app desde su celular."""
    if qrcode is None:
        print("Aviso: instala 'qrcode[pil]' (pip install -r requirements.txt) para generar el QR.")
        return
    carpeta = os.path.join(app.static_folder, "img")
    os.makedirs(carpeta, exist_ok=True)
    try:
        imagen = qrcode.make(APP_URL)
        imagen.save(os.path.join(carpeta, "qr.png"))
    except Exception as exc:  # nunca debe tumbar el arranque de la app
        print(f"No se pudo generar la imagen del QR: {exc}")

    print(f"\nEscanea este QR para abrir AquaCajay ({APP_URL}):")
    qr_terminal = qrcode.QRCode(border=1)
    qr_terminal.add_data(APP_URL)
    qr_terminal.print_ascii(invert=True)
    print()


generar_qr()  # se genera al importar el módulo, funcione localmente o en un servidor


if __name__ == "__main__":
    # Abre el navegador automáticamente al iniciar (solo una vez).
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        webbrowser.open("http://127.0.0.1:5000/")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )