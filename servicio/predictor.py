"""Clasificador de síntomas que hace de modelo, para el servicio del médico.

Todavía no hay un modelo entrenado. El módulo cumple el contrato del
servicio: cuatro datos clínicos de entrada y uno de cuatro estados de salida.
Los umbrales son explícitos para que cada estado se pueda alcanzar y cada
dato pueda cambiar el resultado.

La evolución crónica se evalúa primero. Una evolución de 90 días o más
define ENFERMEDAD CRÓNICA aunque el cuadro actual también sea intenso.
La enfermedad aguda es un cuadro intenso y más corto.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

STATE_HEALTHY = "NO ENFERMO"
STATE_MILD = "ENFERMEDAD LEVE"
STATE_ACUTE = "ENFERMEDAD AGUDA"
STATE_CHRONIC = "ENFERMEDAD CRÓNICA"

STATES = (STATE_HEALTHY, STATE_MILD, STATE_ACUTE, STATE_CHRONIC)

MODEL_VERSION = "0.1.0"

FEVER_MIN = 34.0
FEVER_MAX = 43.0
PAIN_MIN = 0
PAIN_MAX = 10
DAYS_MIN = 0
DAYS_MAX = 3650
SYMPTOM_COUNT_MIN = 0
SYMPTOM_COUNT_MAX = 30

CHRONIC_MIN_DAYS = 90
ACUTE_MIN_FEVER = 38.5
ACUTE_MIN_PAIN = 7
ACUTE_MIN_SYMPTOMS = 5
HEALTHY_MAX_FEVER = 37.5
HEALTHY_MAX_PAIN = 2
HEALTHY_MAX_SYMPTOMS = 1
HEALTHY_MAX_DAYS = 3

FIELD_FEVER = "fiebre"
FIELD_PAIN = "intensidad_dolor"
FIELD_DAYS = "dias_sintomas"
FIELD_SYMPTOMS = "numero_sintomas"


class PredictionInputError(ValueError):
    """Falta un dato, no es numérico o está fuera del rango aceptado."""

    def __init__(self, message: str, field: str) -> None:
        super().__init__(message)
        self.field = field


@dataclass(frozen=True)
class Prediction:
    state: str
    rule: str
    fever_celsius: float
    pain_intensity: int
    symptom_days: int
    symptom_count: int

    @property
    def state_class(self) -> str:
        return {
            STATE_HEALTHY: "sano",
            STATE_MILD: "leve",
            STATE_ACUTE: "aguda",
            STATE_CHRONIC: "cronica",
        }[self.state]


@dataclass(frozen=True)
class Example:
    fever_celsius: float
    pain_intensity: int
    symptom_days: int
    symptom_count: int
    expected_state: str


# Un conjunto de parámetros por estado. Lo usan las pruebas y el formulario.
EXAMPLES: tuple[Example, ...] = (
    Example(36.6, 1, 1, 0, STATE_HEALTHY),
    Example(37.6, 4, 4, 2, STATE_MILD),
    Example(39.2, 8, 2, 6, STATE_ACUTE),
    Example(37.0, 3, 120, 2, STATE_CHRONIC),
)


def rule_lines() -> list[str]:
    """Reglas que ve el médico. Los números salen de las constantes."""
    return [
        (
            f"{STATE_CHRONIC} si los días con síntomas son {CHRONIC_MIN_DAYS} o más. "
            "Esta condición se mira primero."
        ),
        (
            f"{STATE_ACUTE} si la fiebre es {ACUTE_MIN_FEVER:g} °C o más, "
            f"el dolor es {ACUTE_MIN_PAIN} o más, "
            f"o el número de síntomas es {ACUTE_MIN_SYMPTOMS} o más."
        ),
        (
            f"{STATE_HEALTHY} si la fiebre es menor de {HEALTHY_MAX_FEVER:g} °C, "
            f"el dolor es {HEALTHY_MAX_PAIN} o menos, "
            f"los síntomas son {HEALTHY_MAX_SYMPTOMS} o menos "
            f"y los días son {HEALTHY_MAX_DAYS} o menos."
        ),
        f"{STATE_MILD} en cualquier otro caso dentro de los rangos aceptados.",
    ]


def predict_state(
    fever_celsius: object,
    pain_intensity: object,
    symptom_days: object,
    symptom_count: object,
) -> str:
    """Devuelve un estado clínico a partir de cuatro datos de síntomas.

    Acepta números o textos numéricos. El formulario envía texto y la fiebre
    admite coma decimal. Casos que alcanzan cada estado:

    predict_state(36.6, 1, 1, 0) -> NO ENFERMO
    predict_state(37.6, 4, 4, 2) -> ENFERMEDAD LEVE
    predict_state(39.2, 8, 2, 6) -> ENFERMEDAD AGUDA
    predict_state(37.0, 3, 120, 2) -> ENFERMEDAD CRÓNICA
    """
    return predict_details(
        fever_celsius,
        pain_intensity,
        symptom_days,
        symptom_count,
    ).state


def predict_details(
    fever_celsius: object,
    pain_intensity: object,
    symptom_days: object,
    symptom_count: object,
) -> Prediction:
    """Clasifica y conserva la regla activada, para la página y el API."""
    fever = _as_fever(fever_celsius)
    pain = _as_int(pain_intensity, FIELD_PAIN, "La intensidad del dolor", PAIN_MIN, PAIN_MAX)
    days = _as_int(symptom_days, FIELD_DAYS, "Los días con síntomas", DAYS_MIN, DAYS_MAX)
    symptoms = _as_int(
        symptom_count,
        FIELD_SYMPTOMS,
        "El número de síntomas",
        SYMPTOM_COUNT_MIN,
        SYMPTOM_COUNT_MAX,
    )
    state, rule = _classify(fever, pain, days, symptoms)
    return Prediction(state, rule, fever, pain, days, symptoms)


def read_features(features: Mapping[str, object]) -> tuple[object, object, object, object]:
    """Toma las cuatro entradas de un diccionario. Las claves están en español."""
    fever = _lookup(features, (FIELD_FEVER,), FIELD_FEVER, "Indique la fiebre en °C.")
    pain = _lookup(
        features,
        (FIELD_PAIN, "dolor"),
        FIELD_PAIN,
        "Indique la intensidad del dolor de 0 a 10.",
    )
    days = _lookup(
        features,
        (FIELD_DAYS, "dias"),
        FIELD_DAYS,
        "Indique los días con síntomas.",
    )
    symptoms = _lookup(
        features,
        (FIELD_SYMPTOMS, "sintomas"),
        FIELD_SYMPTOMS,
        "Indique el número de síntomas.",
    )
    return fever, pain, days, symptoms


def _lookup(features: Mapping[str, object], keys: tuple[str, ...], field: str, message: str) -> object:
    for key in keys:
        if key not in features:
            continue
        value = features[key]
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return value
    raise PredictionInputError(f"{message} Este dato es obligatorio.", field)


def _as_fever(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise PredictionInputError("La fiebre debe ser un número en °C.", FIELD_FEVER)
    if isinstance(value, str):
        try:
            fever = float(value.strip().replace(",", "."))
        except ValueError as exc:
            raise PredictionInputError("La fiebre debe ser un número en °C.", FIELD_FEVER) from exc
    else:
        fever = float(value)
    if math.isnan(fever) or math.isinf(fever):
        raise PredictionInputError("La fiebre debe ser un número en °C.", FIELD_FEVER)
    if fever < FEVER_MIN or fever > FEVER_MAX:
        raise PredictionInputError(
            f"La fiebre debe estar entre {FEVER_MIN:g} y {FEVER_MAX:g} °C.",
            FIELD_FEVER,
        )
    return fever


def _as_int(value: object, field: str, label: str, low: int, high: int) -> int:
    if isinstance(value, bool):
        raise PredictionInputError(f"{label} debe ser un número entero.", field)
    if isinstance(value, int):
        number = value
    elif isinstance(value, float):
        if math.isnan(value) or math.isinf(value) or not value.is_integer():
            raise PredictionInputError(f"{label} debe ser un número entero.", field)
        number = int(value)
    elif isinstance(value, str):
        try:
            parsed = float(value.strip().replace(",", "."))
        except ValueError as exc:
            raise PredictionInputError(f"{label} debe ser un número entero.", field) from exc
        if math.isnan(parsed) or math.isinf(parsed) or not parsed.is_integer():
            raise PredictionInputError(f"{label} debe ser un número entero.", field)
        number = int(parsed)
    else:
        raise PredictionInputError(f"{label} debe ser un número entero.", field)
    if number < low or number > high:
        raise PredictionInputError(f"{label} debe estar entre {low} y {high}.", field)
    return number


def _classify(fever: float, pain: int, days: int, symptoms: int) -> tuple[str, str]:
    if days >= CHRONIC_MIN_DAYS:
        return (
            STATE_CHRONIC,
            f"Evolución de {days} días (umbral crónico: {CHRONIC_MIN_DAYS} días o más).",
        )

    reasons: list[str] = []
    if fever >= ACUTE_MIN_FEVER:
        reasons.append(f"fiebre de {fever:g} °C")
    if pain >= ACUTE_MIN_PAIN:
        reasons.append(f"dolor {pain}/10")
    if symptoms >= ACUTE_MIN_SYMPTOMS:
        reasons.append(f"{symptoms} síntomas")
    if reasons:
        joined = ", ".join(reasons)
        return STATE_ACUTE, f"Cuadro intenso y de corta evolución: {joined}."

    if (
        fever < HEALTHY_MAX_FEVER
        and pain <= HEALTHY_MAX_PAIN
        and symptoms <= HEALTHY_MAX_SYMPTOMS
        and days <= HEALTHY_MAX_DAYS
    ):
        return (
            STATE_HEALTHY,
            "Fiebre, dolor, duración y número de síntomas están por debajo del umbral de enfermedad.",
        )

    return (
        STATE_MILD,
        "Hay señales de enfermedad, sin intensidad aguda ni evolución crónica.",
    )


def main() -> int:
    failed = False
    for example in EXAMPLES:
        state = predict_state(
            example.fever_celsius,
            example.pain_intensity,
            example.symptom_days,
            example.symptom_count,
        )
        print(state)
        if state != example.expected_state:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
