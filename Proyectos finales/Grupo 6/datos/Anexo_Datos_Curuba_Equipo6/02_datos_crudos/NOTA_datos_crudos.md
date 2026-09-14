# Datos crudos

`exporting-economies_081090.xlsx` — descarga original de Trade Map (ITC), **sin ninguna modificación**.

| Campo | Detalle |
|---|---|
| Consulta | Economías exportadoras de la subpartida 081090 hacia el mundo |
| Estructura | 161 filas (1 fila `Mundo` con código `000` + 160 economías) y 16 columnas |
| Años | 2016 a 2025, una columna por año |
| Unidad | Miles de dólares corrientes (USD Thousand) |
| Descriptor del producto | "Tamarindos frescos, los anacardos, la jaca, litchis, sapotillos, maracuyá, carambola, pitahaya y otros frutos comestibles (exc. frutos de cáscara, bananas, dátiles, higos, piñas, aguacates, guayabas, mangos y mangostanes, papayas, cítricos, uvas, melones, manzanas, membrillos, peras, albaricoques, cerezas, melocotones, ciruelas, endrinas, fresas, frambuesas, moras, zarzamoras, arándanos, kiwi, durians, caqui y grosellas)" |

**No editar este archivo.** Cualquier transformación debe hacerse con los scripts de `07_scripts/`, que
escriben sus resultados en `03_datos_limpios/` y `04_indicadores_reales/`. Así el crudo sigue sirviendo
como punto de partida auditable frente a la fuente original.

La cobertura del año 2025 es parcial (109 de 160 economías) por tratarse del año en curso al momento de
la descarga; para rankings definitivos se usa 2024.
