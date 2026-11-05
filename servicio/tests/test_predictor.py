"""Pruebas de la función que simula el modelo."""

from __future__ import annotations

import unittest

from predictor import (
    EXAMPLES,
    STATES,
    STATE_ACUTE,
    STATE_CHRONIC,
    STATE_HEALTHY,
    STATE_MILD,
    PredictionInputError,
    predict_state,
)


class PruebasDelModelo(unittest.TestCase):
    def test_debe_cubrir_los_cuatro_estados_con_los_casos_canonicos(self) -> None:
        obtenidos = {
            predict_state(
                caso.fever_celsius,
                caso.pain_intensity,
                caso.symptom_days,
                caso.symptom_count,
            )
            for caso in EXAMPLES
        }
        self.assertEqual(obtenidos, set(STATES))

    def test_debe_devolver_el_estado_documentado_de_cada_caso(self) -> None:
        for caso in EXAMPLES:
            estado = predict_state(
                caso.fever_celsius,
                caso.pain_intensity,
                caso.symptom_days,
                caso.symptom_count,
            )
            self.assertEqual(estado, caso.expected_state)

    def test_debe_usar_la_fiebre_para_salir_de_no_enfermo(self) -> None:
        self.assertEqual(predict_state(39.0, 1, 1, 0), STATE_ACUTE)
        self.assertEqual(predict_state(37.8, 1, 1, 0), STATE_MILD)

    def test_debe_usar_el_dolor_para_cambiar_el_estado(self) -> None:
        self.assertEqual(predict_state(36.6, 8, 1, 0), STATE_ACUTE)
        self.assertEqual(predict_state(36.6, 3, 1, 0), STATE_MILD)

    def test_debe_usar_los_dias_y_preferir_cronica_aunque_el_cuadro_sea_intenso(self) -> None:
        self.assertEqual(predict_state(36.6, 1, 120, 0), STATE_CHRONIC)
        self.assertEqual(predict_state(40.0, 9, 100, 6), STATE_CHRONIC)
        self.assertEqual(predict_state(36.6, 1, 90, 0), STATE_CHRONIC)

    def test_debe_usar_el_numero_de_sintomas(self) -> None:
        self.assertEqual(predict_state(36.6, 1, 1, 5), STATE_ACUTE)
        self.assertEqual(predict_state(36.6, 1, 1, 2), STATE_MILD)

    def test_debe_aceptar_texto_con_coma_decimal(self) -> None:
        self.assertEqual(predict_state("36,6", "1", "1", "0"), STATE_HEALTHY)

    def test_debe_rechazar_valores_fuera_de_rango(self) -> None:
        with self.assertRaises(PredictionInputError):
            predict_state(30, 1, 1, 0)
        with self.assertRaises(PredictionInputError):
            predict_state(36.6, 11, 1, 0)
        with self.assertRaises(PredictionInputError):
            predict_state(36.6, 1, -1, 0)
        with self.assertRaises(PredictionInputError):
            predict_state(36.6, 1, 1, 40)


if __name__ == "__main__":
    unittest.main()
