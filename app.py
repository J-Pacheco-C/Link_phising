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

import requests
from flask import Flask, jsonify, render_template, request
from user_agents import parse as parse_user_agent

app = Flask(__name__)

LOG_FILE = "capturas.jsonl"  # un registro (JSON) por línea


def guardar_registro(registro: dict) -> None:
    """Guarda el registro en un archivo .jsonl (uno por línea, fácil de leer)."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def obtener_ip_real() -> str:
    """
    Render (y la mayoría de hostings) ponen tu app detrás de un proxy.
    El header X-Forwarded-For puede traer varias IPs separadas por coma
    (cada "salto" de red); la IP real del usuario es la PRIMERA.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def parsear_user_agent(ua_string: str) -> dict:
    """
    Convierte el string crudo del User-Agent en campos legibles.
    Ej: "Mozilla/5.0 (Windows NT 10.0...) Chrome/154..." ->
        navegador: Chrome, version: 154, sistema_operativo: Windows 10, es_movil: False
    """
    if not ua_string:
        return {
            "navegador": "desconocido",
            "version_navegador": "desconocido",
            "sistema_operativo": "desconocido",
            "es_movil": None,
            "tipo_dispositivo": "desconocido",
        }
    ua = parse_user_agent(ua_string)
    if ua.is_mobile:
        tipo_dispositivo = "móvil"
    elif ua.is_tablet:
        tipo_dispositivo = "tablet"
    elif ua.is_pc:
        tipo_dispositivo = "escritorio"
    else:
        tipo_dispositivo = "otro"
    return {
        "navegador": ua.browser.family,
        "version_navegador": ua.browser.version_string,
        "sistema_operativo": f"{ua.os.family} {ua.os.version_string}".strip(),
        "es_movil": ua.is_mobile,
        "tipo_dispositivo": tipo_dispositivo,
    }


def geolocalizar_ip(ip: str) -> dict:
    """
    Geolocalización PASIVA por IP: solo da precisión de ciudad/región,
    nunca de calle (esa limitación es física, no del servicio).
    Usa ip-api.com, gratis para uso no comercial, sin API key.
    """
    # IPs locales/privadas no se pueden geolocalizar (ej. pruebas en localhost)
    if not ip or ip.startswith(("127.", "10.", "192.168.", "172.")):
        return {"geo_pais": None, "geo_ciudad": None, "geo_region": None, "geo_isp": None}

    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,regionName,city,isp,query"},
            timeout=3,
        )
        data = resp.json()
        if data.get("status") == "success":
            return {
                "geo_pais": data.get("country"),
                "geo_ciudad": data.get("city"),
                "geo_region": data.get("regionName"),
                "geo_isp": data.get("isp"),
            }
    except requests.RequestException:
        pass

    return {"geo_pais": None, "geo_ciudad": None, "geo_region": None, "geo_isp": None}


def capturar_datos_pasivos() -> dict:
    """
    Todo esto se obtiene SOLO con el request HTTP (headers + IP) más un
    enriquecimiento automático (parseo de user-agent + geolocalización por IP).
    No requiere que el usuario haga nada ni que cargue JavaScript.
    """
    ip = obtener_ip_real()
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": ip,
        "user_agent_crudo": request.headers.get("User-Agent"),
        "idioma": request.headers.get("Accept-Language"),
        "referer": request.headers.get("Referer"),
        "host_solicitado": request.headers.get("Host"),
        "tipo": "pasivo",
    }
    registro.update(parsear_user_agent(request.headers.get("User-Agent")))
    registro.update(geolocalizar_ip(ip))
    return registro


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
    ip = obtener_ip_real()
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": ip,
        "tipo": "activo",
        **datos_cliente,
    }
    # Si el usuario dio permiso de GPS, esos datos (geo_lat/geo_lon) ya vienen
    # en datos_cliente con precisión real de metros — no los pisamos.
    # Si NO dio permiso, al menos dejamos la geolocalización aproximada por IP.
    if "geo_lat" not in registro:
        registro.update(geolocalizar_ip(ip))
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
