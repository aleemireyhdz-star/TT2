# Prototype history and replication assumptions

[Project overview](../README.md) · [Resumen en español](../README.es.md)

## English

The project owner clarified the following on **12 November 2026**. These are historical setup details, not newly repeated measurements.

| Item | Historical prototype | Implication for replication |
| --- | --- | --- |
| Physical availability | The prototype operated at the January 2026 defense and was subsequently dismantled. | New tests on that assembly are unavailable. Rebuilding it is not a prerequisite for the software demonstration. |
| Firmware | The owner confirms compilation and physical operation for the defense. The exact historical board profile and build log have not been recovered. | This confirmation is distinct from a reproducible compiler record for the published sketch. |
| Location | No GPS/geolocation hardware was fitted. The school coordinates were fixed manually for the defense; other coordinates were used for demonstration cases. | Set the intended location explicitly. Values in the code or saved configuration are scenario inputs, not a measured device position. |
| Sensor thresholds | The team varied the water height in a container and recorded the assembled prototype's voltage readings to choose the level cutoffs. | The cutoffs belong to that assembly. A different sensor, shunt, ADC, supply or mounting requires its own measurements. |

The retained cutoffs are **0.695, 0.759 and 0.812 V**. They classify sensor levels 0–3; the alert color also depends on the geographic category. They are not universal voltage-to-height calibration constants. The available account does not establish a transferable calibration curve or measurement uncertainty.

For a software demonstration, choose coordinates in the dashboard or send numeric `lat`/`lon` to `POST /api/coords` within the application's supported rectangle. Then send an example voltage/percentage to `POST /ingest`. Changing location waits for a new reading in the updated API. Such requests simulate inputs; they do not locate or measure a physical sensor.

### What can be checked now

- The [automated API/dashboard suite](api-validation.md) checks the post-defense software without a connected ESP32.
- Historical photos, the team report and owner confirmation document the former prototype. A photograph alone does not establish calibration, timing or field performance. The catalogued PF06 clip has only been sampled for solar-tracker motion; it is not treated here as complete end-to-end validation.
- Firmware compilation can be attempted without uploading to a board, once the target profile and toolchain are installed. A November attempt using Arduino CLI 1.2.0, ESP32 core 3.3.3 and the provisional `esp32:esp32:esp32` target stopped during SDK installation because temporary storage was exhausted. The compiler did not run; no firmware pass/fail result was obtained. The temporary SDK was removed.

Physical telemetry, sensor calibration and the solar/power assembly cannot be revalidated on the dismantled prototype. This is a documented availability limit, not an outstanding promise of new hardware tests. A future replica would require its own hardware validation.

## Español

El responsable del proyecto aclaró lo siguiente el **12 de noviembre de 2026**. Son detalles históricos del montaje, no mediciones repetidas recientemente.

| Aspecto | Prototipo histórico | Consecuencia al replicarlo |
| --- | --- | --- |
| Disponibilidad física | El prototipo funcionó en la defensa de enero de 2026 y después se desmanteló. | No se pueden repetir pruebas sobre ese montaje. Reconstruirlo no es un requisito para la demostración de software. |
| Firmware | El responsable confirma la compilación y operación física para la defensa. No se han recuperado el perfil exacto de placa ni el registro de compilación de entonces. | Esa confirmación es distinta de un registro de compilación reproducible del sketch publicado. |
| Ubicación | No había hardware GPS/geolocalización. Para la defensa se fijaron manualmente las coordenadas de la escuela; también se utilizaron otras para casos de demostración. | Configurar expresamente la ubicación deseada. Los valores del código o de la configuración guardada representan escenarios, no una posición medida del dispositivo. |
| Umbrales del sensor | El equipo varió la altura del agua en un recipiente y anotó los voltajes del prototipo integrado para definir los cortes de nivel. | Los cortes corresponden a ese montaje. Otro sensor, resistencia, ADC, alimentación o montaje requiere mediciones propias. |

Se conservan los cortes de **0.695, 0.759 y 0.812 V**. Clasifican los niveles 0–3 del sensor; el color de alerta también depende de la categoría geográfica. No son constantes universales de conversión de voltaje a altura. La información disponible no establece una curva de calibración transferible ni una incertidumbre de medida.

En la demostración de software se pueden elegir coordenadas en la interfaz o enviar `lat`/`lon` numéricos a `POST /api/coords` dentro del rectángulo admitido. Después se envían voltaje/porcentaje de ejemplo a `POST /ingest`. En la API actualizada, cambiar la ubicación requiere una lectura nueva. Estas peticiones simulan entradas; no localizan ni miden un sensor físico.

### Qué se puede comprobar ahora

- La [suite automatizada de API/interfaz](api-validation.md) comprueba el software posterior a la defensa sin una ESP32 conectada.
- Las fotos históricas, la memoria del equipo y la confirmación del responsable documentan el prototipo que existió. Una fotografía por sí sola no demuestra calibración, tiempos o desempeño de campo. Del video catalogado como PF06 solo se han muestreado escenas del movimiento del seguidor solar; aquí no se considera una validación completa de extremo a extremo.
- Se puede intentar compilar el firmware sin cargarlo en una placa, una vez instalados el perfil y las herramientas. Un intento de noviembre con Arduino CLI 1.2.0, núcleo ESP32 3.3.3 y destino provisional `esp32:esp32:esp32` se detuvo al instalar el SDK por falta de espacio temporal. El compilador no llegó a ejecutarse; no se obtuvo un resultado favorable o desfavorable del firmware. El SDK temporal se retiró.

La telemetría física, la calibración del sensor y el conjunto solar/de alimentación no pueden volver a comprobarse sobre el prototipo desmantelado. Es un límite documentado de disponibilidad, no una promesa pendiente de nuevas pruebas físicas. Una réplica futura necesitaría su propia validación de hardware.

## Tool references / Referencias de herramientas

- [Arduino CLI compile command](https://arduino.github.io/arduino-cli/1.2/commands/arduino-cli_compile/)
- [Espressif Arduino core installation](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
