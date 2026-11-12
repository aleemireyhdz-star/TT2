"""Water-level API; portfolio hardening of the academic prototype."""

from datetime import datetime, timezone
import json
import logging
import math
import os
from pathlib import Path
import tempfile
from threading import RLock
from time import monotonic

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from Realtime import (
    LATITUD_FIJA,
    LONGITUD_FIJA,
    predecir_alerta_con_coordenadas,
    validar_coordenadas_cdmx,
)


def _json_object():
    if not request.is_json:
        raise UnsupportedMediaType(description="Se requiere Content-Type application/json.")
    try:
        data = request.get_json()
    except BadRequest as exc:
        raise BadRequest(description="El cuerpo debe ser JSON válido.") from exc
    if not isinstance(data, dict):
        raise BadRequest(description="El cuerpo JSON debe ser un objeto.")
    return data


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BadRequest(description=f"{name} debe ser un número finito.")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise BadRequest(description=f"{name} debe ser un número finito.") from exc
    if not math.isfinite(number):
        raise BadRequest(description=f"{name} debe ser un número finito.")
    return number


def _coordinates(lat, lon):
    lat = _number(lat, "lat")
    lon = _number(lon, "lon")
    if not validar_coordenadas_cdmx(lat, lon):
        raise BadRequest(description="Coordenadas fuera del rango geográfico admitido.")
    return {"latitud": lat, "longitud": lon}


def _save_coordinates(path, coordinates):
    """Replace the config atomically; leave the old file intact on failure."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(coordinates, stream, allow_nan=False)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def create_app(config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        COORDS_CONFIG_FILE=Path(__file__).resolve().parent / "coords_config.json",
        SENSOR_MAX_AGE_SECONDS=30.0,
    )
    if config:
        app.config.update(config)
    max_age = float(app.config["SENSOR_MAX_AGE_SECONDS"])
    if not math.isfinite(max_age) or max_age <= 0:
        raise ValueError("SENSOR_MAX_AGE_SECONDS must be positive and finite")
    config_path = Path(app.config["COORDS_CONFIG_FILE"])
    coordinates = _coordinates(LATITUD_FIJA, LONGITUD_FIJA)
    if config_path.exists():
        try:
            saved = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(saved, dict):
                raise ValueError("Coordinate configuration is not an object")
            coordinates = _coordinates(saved.get("latitud"), saved.get("longitud"))
        except (OSError, ValueError, BadRequest):
            app.logger.warning("Invalid coordinate configuration; using defaults.")

    lock = RLock()
    latest = None
    received_at = None
    received_monotonic = None

    @app.errorhandler(BadRequest)
    @app.errorhandler(UnsupportedMediaType)
    def invalid_request(error):
        return jsonify(ok=False, error=error.description), error.code

    @app.after_request
    def prevent_cached_status(response):
        if request.path.startswith("/api/") or request.path == "/ingest":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/ingest")
    def ingest():
        nonlocal latest, received_at, received_monotonic
        data = _json_object()
        voltage = _number(data.get("v"), "v")
        percentage = _number(data.get("pct"), "pct")
        if not 0.0 <= voltage <= 3.3:
            raise BadRequest(description="v debe estar entre 0 y 3.3 V.")
        if not 0.0 <= percentage <= 100.0:
            raise BadRequest(description="pct debe estar entre 0 y 100.")

        # Preserve the academic voltage thresholds and geographic alert rules.
        if voltage <= 0.695:
            level = 0
        elif voltage <= 0.759:
            level = 1
        elif voltage <= 0.812:
            level = 2
        else:
            level = 3
        with lock:
            try:
                result = predecir_alerta_con_coordenadas(
                    coordinates["latitud"], coordinates["longitud"], level
                )
            except Exception:
                app.logger.exception("Unable to compute the alert.")
                return jsonify(ok=False, error="No se pudo calcular la alerta."), 503
            latest = result
            received_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            received_monotonic = monotonic()
        return jsonify(ok=True)

    @app.get("/api/status")
    def status():
        with lock:
            age = None if received_monotonic is None else max(0.0, monotonic() - received_monotonic)
            fresh = latest is not None and age < max_age
            if fresh:
                result = dict(latest)
            else:
                result = {
                    "alerta": "GRIS",
                    "riesgo_zona": "DESCONOCIDO",
                    "riesgo_score": 0,
                    "nivel_sensor": -1,
                    "coordenadas": dict(coordinates),
                    "mensaje": (
                        "Sin recepción reciente del sensor."
                        if latest is not None else "Esperando datos del sensor..."
                    ),
                }
            result.update(
                data_status="fresh" if fresh else ("stale" if latest is not None else "waiting"),
                received_at=received_at,
                age_seconds=None if age is None else round(age, 3),
            )
        return jsonify(result)

    @app.get("/api/coords")
    def get_coordinates():
        with lock:
            return jsonify(coordinates)

    @app.post("/api/coords")
    def set_coordinates():
        nonlocal coordinates, latest, received_at, received_monotonic
        data = _json_object()
        candidate = _coordinates(data.get("lat"), data.get("lon"))
        with lock:
            try:
                _save_coordinates(config_path, candidate)
            except OSError:
                app.logger.exception("Unable to save coordinates.")
                return jsonify(ok=False, error="No se pudieron guardar las coordenadas."), 500
            if candidate != coordinates:
                coordinates = candidate
                latest = received_at = received_monotonic = None
            return jsonify(ok=True, coordenadas=coordinates)

    return app


# Existing Flask CLI and wsgi.py imports continue to expose `app`.
app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode, use_reloader=False)
