"""
Proyecto educativo - Clase de Ciberseguridad
Demuestra cómo un simple link puede recolectar datos de forma:
  - PASIVA: lo que viaja automáticamente en el request HTTP (headers, IP)
  - ACTIVA: lo que se obtiene ejecutando JavaScript en el navegador de quien
            abre el link (requiere que la página cargue)

USO ÉTICO: solo para entorno de evaluación controlado, con consentimiento
de quien abre el link (tu profesor / compañeros informados).
"""

import json
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

LOG_FILE = "capturas.jsonl"  # un registro (JSON) por línea


def guardar_registro(registro: dict) -> None:
    """Guarda el registro en un archivo .jsonl (uno por línea, fácil de leer)."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def capturar_datos_pasivos() -> dict:
    """
    Todo esto viaja SOLO en los headers HTTP / capa TCP del request.
    No requiere que el usuario haga nada ni que cargue JavaScript.
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
        "idioma": request.headers.get("Accept-Language"),
        "referer": request.headers.get("Referer"),
        "host_solicitado": request.headers.get("Host"),
        "tipo": "pasivo",
    }


@app.route("/")
def index():
    """
    Este es el link que compartes. Al entrar:
    1) Se capturan y guardan los datos pasivos (automático).
    2) Se sirve una página con JS que, con un botón de consentimiento,
       manda datos activos al endpoint /registrar-activo.
    """
    datos_pasivos = capturar_datos_pasivos()
    guardar_registro(datos_pasivos)
    return render_template("index.html")


@app.route("/registrar-activo", methods=["POST"])
def registrar_activo():
    """
    Recibe los datos que el JavaScript del navegador de la víctima
    recolectó usando APIs del propio navegador (screen, Intl, etc.)
    y, si el usuario aceptó, geolocalización.
    """
    datos_cliente = request.get_json(silent=True) or {}
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "tipo": "activo",
        **datos_cliente,
    }
    guardar_registro(registro)
    return jsonify({"status": "ok"})


@app.route("/dashboard")
def dashboard():
    """
    Vista simple para ver todo lo capturado durante tu demo/presentación.
    (Para producción real esto debería tener contraseña; aquí es solo demo académica.)
    """
    registros = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                registros.append(json.loads(linea))
    return render_template("dashboard.html", registros=registros)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
