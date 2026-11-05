"""Pruebas de la página y del API."""

from __future__ import annotations

import unittest

from app import create_app
from predictor import EXAMPLES


class PruebasDelServicio(unittest.TestCase):
    def setUp(self) -> None:
        self.cliente = create_app().test_client()

    def test_debe_mostrar_el_formulario(self) -> None:
        respuesta = self.cliente.get("/")
        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.get_data(as_text=True)
        for caso in EXAMPLES:
            self.assertIn(caso.expected_state, cuerpo)

    def test_debe_devolver_cada_estado_por_json(self) -> None:
        for caso in EXAMPLES:
            respuesta = self.cliente.post(
                "/api/predecir",
                json={
                    "fiebre": caso.fever_celsius,
                    "intensidad_dolor": caso.pain_intensity,
                    "dias_sintomas": caso.symptom_days,
                    "numero_sintomas": caso.symptom_count,
                },
            )
            self.assertEqual(respuesta.status_code, 200, respuesta.get_data(as_text=True))
            self.assertEqual(respuesta.get_json()["estado"], caso.expected_state)

    def test_debe_devolver_cada_estado_por_enlace(self) -> None:
        for caso in EXAMPLES:
            respuesta = self.cliente.get(
                "/api/predecir",
                query_string={
                    "fiebre": caso.fever_celsius,
                    "intensidad_dolor": caso.pain_intensity,
                    "dias_sintomas": caso.symptom_days,
                    "numero_sintomas": caso.symptom_count,
                },
            )
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.get_json()["estado"], caso.expected_state)

    def test_debe_mostrar_el_estado_en_la_pagina(self) -> None:
        for caso in EXAMPLES:
            respuesta = self.cliente.post(
                "/predecir",
                data={
                    "fiebre": caso.fever_celsius,
                    "intensidad_dolor": caso.pain_intensity,
                    "dias_sintomas": caso.symptom_days,
                    "numero_sintomas": caso.symptom_count,
                },
            )
            self.assertEqual(respuesta.status_code, 200)
            self.assertIn(caso.expected_state, respuesta.get_data(as_text=True))

    def test_debe_rechazar_fiebre_fuera_de_rango(self) -> None:
        respuesta = self.cliente.post(
            "/api/predecir",
            json={
                "fiebre": 30,
                "intensidad_dolor": 1,
                "dias_sintomas": 1,
                "numero_sintomas": 0,
            },
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("error", respuesta.get_json())

    def test_debe_informar_que_el_servicio_esta_disponible(self) -> None:
        respuesta = self.cliente.get("/salud")
        self.assertEqual(respuesta.get_json()["estado"], "disponible")


if __name__ == "__main__":
    unittest.main()
