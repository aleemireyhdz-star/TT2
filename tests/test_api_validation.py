"""Regression tests against the actual Flask routes and published model."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import Flask_Server as server

HIGH_ZONE = {"lat": 19.5228166649, "lon": -99.1678551529}
OTHER_ZONE = {"lat": 19.4326, "lon": -99.1332}


class ApiValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "coords.json"
        self.clock = 1000.0
        clock = patch("Flask_Server.monotonic", side_effect=lambda: self.clock)
        clock.start()
        self.addCleanup(clock.stop)
        output = redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)
        self.app = self.make_app()
        previous = self.app.logger.disabled
        self.app.logger.disabled = True
        self.addCleanup(setattr, self.app.logger, "disabled", previous)
        self.client = self.app.test_client()
        self.assertEqual(self.client.post("/api/coords", json=HIGH_ZONE).status_code, 200)

    def make_app(self, **config):
        return server.create_app({
            "TESTING": True, "COORDS_CONFIG_FILE": self.path,
            "SENSOR_MAX_AGE_SECONDS": 30, **config,
        })

    def ingest(self, voltage=0.78, percentage=50):
        return self.client.post("/ingest", json={"v": voltage, "pct": percentage})

    def status(self):
        return self.client.get("/api/status").get_json()

    def assert_error(self, response, code=400):
        self.assertEqual(response.status_code, code)
        self.assertIs(response.get_json()["ok"], False)
        self.assertTrue(response.get_json()["error"])

    def test_initial_status_and_page(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertIn("Última recepción del sensor".encode(), self.client.get("/").data)
        response = self.client.get("/api/status")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        data = response.get_json()
        self.assertEqual((data["alerta"], data["nivel_sensor"], data["data_status"]),
                         ("GRIS", -1, "waiting"))
        self.assertIsNone(data["received_at"])
        self.assertIsNone(data["age_seconds"])

    def test_thirteen_voltage_and_threshold_cases_with_real_alerts(self):
        cases = [(0.65, 0), (0.72, 1), (0.78, 2), (0.85, 3),
                 (0.694999, 0), (0.695, 0), (0.695001, 1),
                 (0.758999, 1), (0.759, 1), (0.759001, 2),
                 (0.811999, 2), (0.812, 2), (0.812001, 3)]
        for voltage, level in cases:
            with self.subTest(voltage=voltage):
                self.assertEqual(self.ingest(voltage).status_code, 200)
                data = self.status()
                self.assertEqual(data["nivel_sensor"], level)
                self.assertEqual(data["riesgo_zona"], "ALTO")
                self.assertEqual(data["alerta"], ["VERDE", "AMARILLO", "ROJO", "ROJO"][level])
                self.assertEqual(data["data_status"], "fresh")

    def test_percentage_boundaries_do_not_replace_voltage_classifier(self):
        for percentage in [0, 100]:
            with self.subTest(percentage=percentage):
                self.assertEqual(self.ingest(0.78, percentage).status_code, 200)
                self.assertEqual(self.status()["nivel_sensor"], 2)

    def test_adc_range_boundaries(self):
        for voltage, level in [(0, 0), (3.3, 3)]:
            with self.subTest(voltage=voltage):
                self.assertEqual(self.ingest(voltage).status_code, 200)
                self.assertEqual(self.status()["nivel_sensor"], level)

    def test_rejects_invalid_voltage_without_losing_last_sample(self):
        self.ingest()
        previous = self.status()
        for value in [None, "0.78", True, False, [], {}, -0.001, 3.300001,
                      float("nan"), float("inf"), -float("inf"), 10**400]:
            with self.subTest(value=repr(value)):
                self.assert_error(self.ingest(value))
                self.assertEqual(self.status(), previous)

    def test_rejects_invalid_percentage(self):
        for value in [None, "50", True, False, [], {}, -0.001, 100.001,
                      float("nan"), float("inf"), -float("inf"), 10**400]:
            with self.subTest(value=repr(value)):
                self.assert_error(self.ingest(percentage=value))

    def test_missing_fields(self):
        for payload in [{}, {"v": 0.78}, {"pct": 50}]:
            with self.subTest(payload=payload):
                self.assert_error(self.client.post("/ingest", json=payload))

    def test_requires_json_objects_on_both_post_routes(self):
        for route in ["/ingest", "/api/coords"]:
            for payload in [[], [1, 2], None, 5, "text", False]:
                with self.subTest(route=route, payload=payload):
                    self.assert_error(self.client.post(
                        route, data=json.dumps(payload), content_type="application/json"))

    def test_malformed_json_and_content_type(self):
        for route in ["/ingest", "/api/coords"]:
            with self.subTest(route=route):
                self.assert_error(self.client.post(route, data="{", content_type="application/json"))
                self.assert_error(self.client.post(route, data="{}", content_type="text/plain"), 415)

    def test_invalid_coordinates_do_not_change_file_or_state(self):
        self.ingest()
        previous, original_file = self.status(), self.path.read_bytes()
        payloads = [{}, {"lat": HIGH_ZONE["lat"]}, {"lon": HIGH_ZONE["lon"]}]
        for key in ["lat", "lon"]:
            for value in [None, True, "19.5", "nan", float("nan"), float("inf"), [], {}, 999, 10**400]:
                payloads.append({**HIGH_ZONE, key: value})
        for payload in payloads:
            with self.subTest(payload=repr(payload)):
                self.assert_error(self.client.post("/api/coords", json=payload))
                self.assertEqual(self.path.read_bytes(), original_file)
                self.assertEqual(self.status(), previous)

    def test_existing_geographic_rectangle_boundaries(self):
        for lat, lon in [(19.35, -99.35), (19.65, -98.95)]:
            self.assertEqual(self.client.post("/api/coords", json={"lat": lat, "lon": lon}).status_code, 200)
        for lat, lon in [(19.349999, -99.2), (19.650001, -99.2), (19.5, -99.350001), (19.5, -98.949999)]:
            self.assert_error(self.client.post("/api/coords", json={"lat": lat, "lon": lon}))

    def test_coordinate_change_waits_for_new_ingestion(self):
        self.ingest()
        self.assertEqual(self.client.post("/api/coords", json=OTHER_ZONE).status_code, 200)
        waiting = self.status()
        self.assertEqual((waiting["alerta"], waiting["data_status"]), ("GRIS", "waiting"))
        self.assertIsNone(waiting["received_at"])
        self.assertEqual(waiting["coordenadas"], {"latitud": OTHER_ZONE["lat"], "longitud": OTHER_ZONE["lon"]})
        self.ingest()
        self.assertEqual(self.status()["coordenadas"], waiting["coordenadas"])
        self.assertEqual(self.status()["data_status"], "fresh")

    def test_resaving_same_coordinates_keeps_sample(self):
        self.ingest()
        previous = self.status()
        self.client.post("/api/coords", json=HIGH_ZONE)
        self.assertEqual(self.status(), previous)

    def test_failed_disk_replace_preserves_file_coordinates_and_sample(self):
        self.ingest()
        previous, original_file = self.status(), self.path.read_bytes()
        with patch("Flask_Server.os.replace", side_effect=OSError("simulated disk error")):
            self.assert_error(self.client.post("/api/coords", json=OTHER_ZONE), 500)
        self.assertEqual(self.path.read_bytes(), original_file)
        self.assertEqual(self.status(), previous)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_expiry_and_refresh_without_sleep(self):
        self.ingest()
        timestamp = self.status()["received_at"]
        self.clock += 29.999
        self.assertEqual(self.status()["data_status"], "fresh")
        self.clock += 0.001
        expired = self.status()
        self.assertEqual((expired["alerta"], expired["data_status"]), ("GRIS", "stale"))
        self.assertEqual(expired["received_at"], timestamp)
        self.assertEqual(expired["age_seconds"], 30)
        self.ingest()
        self.assertEqual((self.status()["data_status"], self.status()["age_seconds"]), ("fresh", 0))

    def test_rejected_input_does_not_refresh_sample_age(self):
        self.ingest()
        self.clock += 29
        self.assert_error(self.ingest(-1))
        self.clock += 1
        self.assertEqual(self.status()["data_status"], "stale")

    def test_model_failure_does_not_acknowledge_or_replace_sample(self):
        self.ingest()
        previous = self.status()
        with patch("Flask_Server.predecir_alerta_con_coordenadas", side_effect=RuntimeError("unavailable")):
            self.assert_error(self.ingest(), 503)
        self.assertEqual(self.status(), previous)

    def test_persisted_coordinates_reload_but_readings_do_not(self):
        self.client.post("/api/coords", json=OTHER_ZONE)
        self.ingest()
        other = self.make_app().test_client()
        self.assertEqual(other.get("/api/coords").get_json(),
                         {"latitud": OTHER_ZONE["lat"], "longitud": OTHER_ZONE["lon"]})
        self.assertEqual(other.get("/api/status").get_json()["data_status"], "waiting")

    def test_invalid_persisted_configuration_uses_valid_defaults(self):
        for text in ["{", "[]", "null", "{}", '{"latitud":999,"longitud":999}',
                     '{"latitud":NaN,"longitud":-99.1}']:
            with self.subTest(text=text):
                self.path.write_text(text)
                client = self.make_app().test_client()
                self.assertEqual(client.get("/api/coords").get_json(),
                                 {"latitud": server.LATITUD_FIJA, "longitud": server.LONGITUD_FIJA})

    def test_app_instances_have_independent_samples(self):
        self.ingest()
        other = self.make_app().test_client()
        self.assertEqual(other.get("/api/status").get_json()["data_status"], "waiting")
        self.assertEqual(self.status()["data_status"], "fresh")

    def test_invalid_expiry_configuration_fails_at_startup(self):
        for age in [0, -1, float("nan"), float("inf")]:
            with self.subTest(age=age), self.assertRaises(ValueError):
                self.make_app(SENSOR_MAX_AGE_SECONDS=age)


if __name__ == "__main__":
    unittest.main()
