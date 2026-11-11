# API validation and regression tests

This is a **post-defense portfolio improvement**, prepared on 10 November 2026. It addresses behaviors reproduced during the October local review. The January 2026 prototype remains identifiable at academic commit `98920f97510750bad523c46adedeeedd7b159b4f`; these changes must not be presented as features or tests completed at that defense.

## Request contract

Both POST routes require `Content-Type: application/json` and a JSON object. Wrong content types return 415; malformed JSON, arrays, scalars, missing fields and invalid values return 400 with `{"ok": false, "error": "..."}`.

| Route | Accepted fields | Behavior |
| --- | --- | --- |
| POST `/ingest` | `v`: finite JSON number in 0–3.3 V; `pct`: finite JSON number in 0–100 | Compute the alert, then acknowledge with `ok:true`. Booleans and numeric strings are rejected. |
| POST `/api/coords` | `lat` and `lon`: finite JSON numbers in the existing geographic rectangle | Save coordinates atomically before changing the in-memory state. |

The geographic rectangle remains latitude 19.35–19.65 and longitude -99.35–-98.95. It is an approximate supported region, not the administrative CDMX polygon. The voltage bounds validate the API's ADC-level input; they do not diagnose 4–20 mA sensor faults or establish calibration accuracy. Percentage is checked but the existing alert classifier still uses voltage.

Valid voltage thresholds, geographic scoring, the dataset lookup, the forest artifact and alert rules are retained. The firmware's numeric JSON payload remains compatible. Coordinate strings previously accepted by float conversion are now rejected deliberately.

If a coordinate file cannot be replaced, the route returns 500 with `ok:false` and retains the previous file, coordinates and sample. If alert computation fails, ingestion returns 503 with `ok:false` and retains the last successful sample. Invalid input never refreshes its age.

## Reception age and coordinate changes

`GET /api/status` adds:

| Field | Meaning |
| --- | --- |
| `data_status` | `waiting`, `fresh` or `stale`. |
| `received_at` | UTC ISO timestamp of the last successfully accepted reading, or null. |
| `age_seconds` | Elapsed monotonic time since that acceptance, or null. |

After **30 seconds without a successful reception**, the default configuration reports GRIS, unknown risk and sensor level -1. The last receipt timestamp remains visible. A new successful ingestion restores a fresh result. `SENSOR_MAX_AGE_SECONDS` is configurable through `create_app`; 30 seconds is a demonstration setting, not a field-validated fault threshold.

Changing coordinates clears the previous reading and returns to waiting until a new ingestion. Saving the same coordinates preserves the current sample. Status responses include `Cache-Control: no-store`.

The dashboard now displays **server receipt time**, preserves zero-valued scores, shows waiting/stale messages and treats HTTP failures as loss of server connection. Polling alone no longer updates the receipt timestamp.

The firmware does not transmit the physical acquisition time. Receipt freshness therefore cannot prove the age of a sample delayed before transmission. The change does not establish uninterrupted offline acquisition or end-to-end sensor health.

## Run the automated checks

Use Python 3.12 in a separate virtual environment. [requirements-api-tests.txt](../requirements-api-tests.txt) records the complete package versions used for this regression run; it preserves the original and October-review requirement files.

```bash
python -m pip install -r requirements-api-tests.txt
python -m unittest discover -s tests -p test_api_validation.py -v
node --test tests/test_dashboard.js
```

The new suite consists of **21 Python test methods** (with subtests, including the 13 original voltage/threshold cases) and **3 JavaScript tests**. Tests call the production Flask routes and use the published model/dataset. Only explicit model-failure and disk-failure cases substitute those dependencies. Each app uses temporary coordinate storage; expiry tests control a monotonic clock rather than sleeping.

Coverage includes malformed bodies, wrong types, non-finite numbers, ranges and boundaries, status transitions, unchanged state on rejection, atomic-save failure, model failure, configuration reload and app-instance isolation. JavaScript tests execute the real dashboard script with small DOM/Leaflet doubles to check receipt-time rendering, stale/waiting messages and HTTP failures.

The regression run passed on Linux with Python 3.12.14, Flask 3.0.0, scikit-learn 1.7.2 and Node 24.22.1. `pip check` also passed. This is software regression coverage, not a browser rendering test, Windows rerun, firmware compilation, new model evaluation or physical measurement.

## Operational limits

The app factory isolates state for tests and uses a lock within an application instance. Latest readings remain in process memory. Multiple server workers would need shared sample/coordinate state and coordinated persistence before being treated as one consistent service. Authentication and public deployment are outside this update.

The [October verification record](verification.md) retains the original observations and model metrics as historical evidence.
