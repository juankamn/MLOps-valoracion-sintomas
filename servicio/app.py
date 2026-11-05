"""Página web y API JSON de la valoración de síntomas."""

from __future__ import annotations

import os
from typing import Mapping

from flask import Flask, jsonify, render_template, request

from predictor import (
    EXAMPLES,
    MODEL_VERSION,
    Prediction,
    PredictionInputError,
    predict_details,
    read_features,
    rule_lines,
)

FORM_KEYS = ("fiebre", "intensidad_dolor", "dias_sintomas", "numero_sintomas")


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False

    @app.get("/")
    def index():
        return render_template("index.html", **_view())

    @app.post("/predecir")
    def predict_form():
        try:
            result = _from_mapping(request.form)
        except PredictionInputError as exc:
            body = _view(error=str(exc), error_field=exc.field, form_values=_sticky(request.form))
            return render_template("index.html", **body), 400
        body = _view(result=result, form_values=_sticky(request.form))
        return render_template("index.html", **body)

    @app.route("/api/predecir", methods=["GET", "POST"])
    def predict_api():
        try:
            result = _from_mapping(_request_mapping())
        except PredictionInputError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(_payload(result))

    @app.get("/salud")
    def health():
        return jsonify({"estado": "disponible"})

    return app


def _from_mapping(features: Mapping[str, object]) -> Prediction:
    fever, pain, days, symptoms = read_features(features)
    return predict_details(fever, pain, days, symptoms)


def _payload(result: Prediction) -> dict[str, object]:
    return {
        "estado": result.state,
        "regla": result.rule,
        "version": MODEL_VERSION,
        "entrada": {
            "fiebre": result.fever_celsius,
            "intensidad_dolor": result.pain_intensity,
            "dias_sintomas": result.symptom_days,
            "numero_sintomas": result.symptom_count,
        },
    }


def _request_mapping() -> Mapping[str, object]:
    if request.method == "POST" and request.is_json:
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            raise PredictionInputError("El cuerpo debe ser un objeto JSON.", "fiebre")
        return body
    if request.method == "POST" and request.form:
        return request.form
    return request.args


def _sticky(features: Mapping[str, object]) -> dict[str, str]:
    values: dict[str, str] = {}
    aliases = {
        "fiebre": ("fiebre",),
        "intensidad_dolor": ("intensidad_dolor", "dolor"),
        "dias_sintomas": ("dias_sintomas", "dias"),
        "numero_sintomas": ("numero_sintomas", "sintomas"),
    }
    for field, keys in aliases.items():
        raw = ""
        for key in keys:
            if key in features and features[key] is not None and str(features[key]).strip() != "":
                raw = str(features[key])
                break
        values[field] = raw
    return values


def _view(
    result: Prediction | None = None,
    error: str | None = None,
    error_field: str | None = None,
    form_values: Mapping[str, str] | None = None,
) -> dict[str, object]:
    sticky = {key: "" for key in FORM_KEYS}
    if form_values:
        sticky.update(form_values)
    return {
        "result": result,
        "error": error,
        "error_field": error_field or "",
        "form_values": sticky,
        "examples": EXAMPLES,
        "rules": rule_lines(),
        "version": MODEL_VERSION,
    }


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    # Todas las interfaces, para que el puerto publicado del contenedor llegue al proceso.
    app.run(host="0.0.0.0", port=port, debug=False)
