# Verification record and known limitations

[Project overview](../README.md) · [Resumen en español](../README.es.md)

## Evidence and reference

This summary is based on the project owner's supplied local review, `Revision_local_TT2.md`, dated **20 October 2026**, and its six-item evidence catalogue. The academic reference is commit [98920f97510750bad523c46adedeeedd7b159b4f](https://github.com/aleemireyhdz-star/TT2/commit/98920f97510750bad523c46adedeeedd7b159b4f).

The results below are **reported local-review results**. The underlying harnesses, JSON records and execution logs referenced by that report have not been included in this repository; they must be added in a sanitized, reviewable form before this record becomes a self-contained reproduction package. Private filesystem paths and personal material are omitted.

The owner's original working copy, Git index and published model were preserved. Tests and retraining used separate copies. No firmware was flashed, public server started or tunnel created. The review exercised Flask's test client rather than the full browser/hardware path.

## Environment

The reported platform was Windows 11 AMD64 with Python 3.12.14.

| Direct dependency | Academic requirements | Review phase A | Review phase B |
| --- | --- | --- | --- |
| scikit-learn | 1.3.2 | 1.3.2 | 1.7.2 |
| pandas | 2.1.4 | 2.1.4 | 2.1.4 |
| NumPy | 1.24.4 | 1.26.4 | 1.26.4 |
| matplotlib | 3.8.2 | 3.8.2 | 3.8.2 |
| Flask | 3.0.0 | 3.0.0 | 3.0.0 |
| joblib | 1.3.2 | 1.3.2 | 1.3.2 |

Installing the original requirements with Python 3.12 and wheels only failed because NumPy 1.24.4 had no compatible wheel in that attempt. This does not establish failure on every Python version.

Both alternative configurations passed `pip check`. The published pickle loaded in phase A with a scikit-learn version warning identifying 1.7.2 as its training version; it loaded in phase B without that warning. The original environment used for the defense was not reconstructed.

[requirements-review-py312.txt](../requirements-review-py312.txt) records the six direct versions from phase B. Complete transitive version locks and verification on other operating systems remain pending. The local launch command in the README is a loopback-only demonstration procedure; that CLI/browser launch was not part of the reported Flask test-client checks.

## API checks

The actual `Flask_Server` application was imported and tested with `app.test_client()`.

| Check | Reported observation |
| --- | --- |
| GET `/` | HTTP 200 with the real HTML template. |
| Initial GET `/api/status` | GRIS, unknown zone, score 0, sensor level -1 and a waiting message. |
| POST/GET `/api/coords` | Coordinates were saved and read back in the disposable copy. |
| Voltage 0.65 / 0.72 / 0.78 / 0.85 V | Levels 0 / 1 / 2 / 3; for the tested ALTO zone, VERDE / AMARILLO / ROJO / ROJO. |
| Each boundary ±0.000001 V | Nine comparisons matched the thresholds below. |

There were **13 explicit sensor-level checks**, not 13 checks covering every component.

| Sensor level | Voltage rule |
| --- | --- |
| 0 | v ≤ 0.695 V |
| 1 | 0.695 V < v ≤ 0.759 V |
| 2 | 0.759 V < v ≤ 0.812 V |
| 3 | v > 0.812 V |

The current server classifies **voltage**, not the supplied percentage. Coordinates drive geographic scoring; rainfall intensity is part of the derived dataset rather than a live weather input.

### Reproduced edge cases to address

- Missing, textual or malformed ingestion values can return HTTP 200/`ok:true` while leaving the previous state untouched.
- Out-of-range values, booleans and non-finite numbers are not consistently rejected.
- JSON arrays can trigger HTTP 500 because handlers expect objects.
- The geographic check uses a bounding rectangle and only warns for out-of-range coordinates; those coordinates can still be saved and scored. Non-finite coordinates can also lead to invalid state or errors.
- A coordinate change does not replace the previous alert result until another ingestion.
- Code inspection shows no sensor-reading expiry in the current status response. The frontend refresh time reflects polling, rather than a sensor acquisition timestamp.

These observations belong to the academic version; this documentation change does not repair or redefine its API behavior.

### Historical diagnostic scripts

Some scripts repeat alert/model logic internally and print success-style messages without asserting expected outcomes. They are diagnostics, not evidence of complete API coverage.

In particular, `python prueba_final.py` from `tests/` failed to find `modelo_predictivo.pkl`. Running it from `src/` as `python ../tests/prueba_final.py` completed, but completion alone did not validate the API. A printed expected score of 42.2 differed from the model's roughly 46.2 in that diagnostic. A future test suite should call production functions/routes and fail on mismatches.

## Model evaluation

The published training script was executed in a disposable copy with a noninteractive plotting backend. Retrained artifacts did not replace the published pickle.

| Configuration | Train/test rows | MSE | R² | RMSE |
| --- | --- | --- | --- | --- |
| scikit-learn 1.3.2, published processed CSV | 244 / 62 | 31.168269848 | 0.694422336 | 5.582854991 |
| scikit-learn 1.3.2, regenerated CSV | 244 / 62 | 31.168269848 | 0.694422336 | 5.582854991 |
| scikit-learn 1.7.2, regenerated CSV | 244 / 62 | 31.168269848 | 0.694422336 | 5.582854991 |

Parameters: 100 trees, maximum depth 10, model seed 42, 20% random test split with seed 42. Inputs: latitude/longitude. Target: `riesgo_zona_score`.

Preprocessing reduced 612 source rows to 306 processed rows; the regenerated CSV differed in bytes but matched the published DataFrame. The review counted 228 ALTO, 58 MEDIO and 20 BAJO rows.

The target is constructed as **0.6 × mapped rainfall intensity + 0.4 × mapped floodable-area percentage**, using numeric values assigned to categorical ranges. The final report describes synthetic/derived data with Atlas de Riesgos / SGIRPC / CDMX open-data background. Exact source resources, versions and preparation lineage remain unresolved.

Important interpretation:

- R²≈0.694 is a reported re-run result for this target and split, not a percentage of flood-prediction accuracy.
- RMSE is measured in score points, not a confidence interval.
- R²≈0.85+ in the former README was not corroborated.
- A diagnostic of the published pickle on the same 62 selected rows gave MSE 32.383710492 and R² 0.682506002. Its original training-row membership is unknown, so this is not a certified held-out evaluation of that artifact.
- At runtime, `Realtime` first looks up a nearby dataset record within 0.0001° and uses the forest when no match is found. Demonstrating an alert at a known dataset coordinate does not independently validate the forest.
- This experiment has no temporal or spatially independent holdout establishing future flood events, calibrated probabilities, lead time or field performance.

## Firmware and physical evidence

The local `Sensor.ino` matched the Git blob after normalizing line endings. Static inspection confirms a 150 Ω shunt, 1,000-reading average, voltage/percentage telemetry, SD logging using uptime, and a 10-second delay after each cycle. Wi-Fi reconnection can block acquisition; continuous offline sampling is not established.

Arduino CLI 1.2.0 and ESP32 core 3.3.3 were located. Compilation attempts with a provisional ESP32 Dev Module profile were blocked before the compiler started by Windows error #623. The historical board profile and compiler success remain unconfirmed.

A partial local solar-tracker sketch and a more complete text listing in the final report (AP.20) were found. Their differences do not establish which source was flashed. They have not been promoted to a recovered final firmware release.

The evidence catalogue identifies:

| ID | Candidate | What it can show |
| --- | --- | --- |
| PF01 | Laboratory prototype photo | Panel/tracker/enclosure integration; the complete base is outside the frame. |
| PF02 | Electronics interior photo | Power components, boards and wiring. |
| PF03 | Sensor-in-water photo | A physical water-test arrangement, without a known-height result by itself. |
| PF04 | PCB top-layout PDF | Placement/connectors, rather than a complete schematic. |
| PF05 | Final team report extracts | Historical 0–55 cm water tests, solar mechanism and energy observations. |
| PF06 | Exterior video | An approximately 185.5-second clip sampled at four points; full audio and recording attribution remain unresolved. |

The visual update includes PF02 and PF03 as unchanged JPEGs, plus a public derivative of PF04 and its rendered preview. [Media provenance and preparation](assets/README.md) records the source mapping and PDF treatment. PF01, PF05 and PF06 remain outside the current public selection. The general overview photograph needs further preparation; report extracts and the video remain to be selected/reviewed. Historic report tests stay distinct from newly repeated measurements.

## Next implementation work

1. Add the actual API-check harness, sanitized output and a complete environment record.
2. Correct input validation, error responses, stale-state handling and tests in a separate behavior-change proposal.
3. Separate local connection configuration from firmware source; rotate any exposed credential that is still in use.
4. Confirm the ESP32 board configuration and obtain a successful build log.
5. Extend the selected physical evidence when the general overview, report extracts and video are ready; retain accurate captions and team credits.
6. Resolve dataset provenance and the license documentation referenced by the original README.
