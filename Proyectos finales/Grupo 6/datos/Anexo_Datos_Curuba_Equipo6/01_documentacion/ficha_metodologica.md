# Ficha metodológica

Producto verificable del **Objetivo específico 1** de la ficha técnica: declaración de fuentes, años,
supuestos y procedimientos de depuración.

## 1. Objeto del estudio

| Elemento | Definición |
|---|---|
| Producto | Curuba (*Passiflora mollissima* Bailey; sin. *Passiflora tripartita* var. *mollissima*) |
| Subpartida arancelaria | NANDINA 0810.90.10.40 (Colombia); a seis dígitos del Sistema Armonizado, 0810.90 |
| Unidad de análisis | Flujos de comercio exterior por economía reportante |
| Unidad monetaria | Miles de dólares corrientes (USD miles) |
| Cobertura temporal | 2016-2025 en los datos primarios de Trade Map; 2019-2024 en los conjuntos estimados por el equipo |
| Cobertura geográfica | 160 economías exportadoras más el agregado Mundo |

**Advertencia de agregación.** La subpartida 081090 no aísla la curuba. Su descriptor oficial es
*"Tamarindos frescos, los anacardos, la jaca, litchis, sapotillos, maracuyá, carambola, pitahaya y otros
frutos comestibles"*, de modo que la curuba viaja agregada con otras frutas exóticas. Ninguna estadística
oficial a seis dígitos permite separarla. De ahí el supuesto de imputación documentado en S1 del registro
de supuestos, y de ahí que el informe final deba contrastarlo con el detalle transaccional de Legiscomex.

## 2. Fuentes

| Fuente | Uso en el estudio | Estado en este anexo |
|---|---|---|
| Trade Map (ITC) | Exportaciones mundiales de 081090 por economía, 2016-2025 | Descargado e incorporado |
| Banco Mundial — World Development Indicators | PIB, TRM, IPC y comercio total de bienes y servicios | Pendiente de descarga |
| Agronet — MinAgricultura (Red SISA) | Producción, área y rendimiento de pasifloras y curuba | Pendiente de descarga |
| Legiscomex | Detalle transaccional: precio FOB, importador, ruta | Pendiente (acceso institucional EAN) |

## 3. Procedimientos de depuración aplicados

1. **Separación del agregado mundial.** La fila con código `000` (Mundo) se extrae a su propia tabla
   (`t3_mundo_081090.csv`) y se excluye del ranking de economías. Dejarla mezclada convertiría al mundo
   entero en el mayor exportador.
2. **Códigos como texto.** Los códigos de economía se leen como cadena para no perder los ceros a la
   izquierda (`040` no debe volverse `40`), lo que rompería cualquier cruce posterior con otra base.
3. **Eliminación de columnas constantes.** `partnerCd`, `partnerLabel`, `productCd` y `productLabel`
   repiten el mismo valor en las 161 filas; su contenido se conserva como metadato en esta ficha y se
   retira de las tablas de trabajo.
4. **Formato ancho y formato largo.** Se entregan ambos: el ancho para lectura humana y el largo
   (*tidy*: una fila por economía y año) para el procesamiento con pandas.
5. **Tratamiento de faltantes.** No se imputan ceros sobre valores ausentes. Una celda vacía significa
   "la economía no reportó", que no es lo mismo que "no exportó". La cobertura anual se documenta en
   `r6_cobertura_y_calidad.csv`.
6. **Año de referencia.** El año 2025 tiene cobertura parcial (109 de 160 economías, 68,1 %), por ser el
   año en curso al momento de la descarga. Para rankings y comparaciones definitivas se usa **2024**
   (139 economías, 86,9 %).

## 4. Indicadores y fórmulas

| Indicador | Fórmula | Rango / umbral | Objetivo |
|---|---|---|---|
| Participación de mercado | Xᵢ / X_mundo × 100 | % | Transversal |
| Índice de Balanza Comercial Relativa (IBCR) | (X − M) / (X + M) | [−1, 1]; 0 = equilibrio | 2 |
| Índice de Apertura Comercial (IAC) | (X + M) / PIB × 100 | > 60 % apertura alta | 2 |
| Coeficiente de Exportación (CE) | X / Producción × 100 | > 50 % industria exportadora | 2 |
| Herfindahl-Hirschman (HHI) | Σ Sⱼ² | > 0,18 concentrado; < 0,15 fragmentado | 3 |
| Número equivalente | 1 / HHI | número de competidores de tamaño equivalente | 3 |
| Índice de Theil | (1/n) Σ (xᵢ/μ) ln(xᵢ/μ) | 0 = distribución homogénea | 3 |
| Grubel-Lloyd (GL) | 1 − \|X − M\| / (X + M) = 1 − \|IBCR\| | 1 = intraindustrial puro; 0 = una sola vía | 3 |
| Balassa (RCA) | (xᵢ/X) / (xᵢᵂ/Xᵂ) | > 1 ventaja comparativa | 4 |
| RSCA | (RCA − 1) / (RCA + 1) | [−1, 1]; > 0 ventaja | 4 |
| Lafay (LFI) | (IBCRᵢ − IBCR_país) × (xᵢ + mᵢ) / (X + M) | suma cero entre productos | 4 |

## 5. Bases de cálculo declaradas

Dos tablas de la ficha técnica usan bases distintas y no deben compararse entre sí sin advertirlo:

| Base | Alcance | X | M | IBCR | GL |
|---|---|---|---|---|---|
| `d1` | Subpartida 0810.90 agregada, Colombia | 2.091,3 | 450,0 | +0,646 | 0,354 |
| `d2` | Curuba específica, Colombia | 2.091,3 | 22,19 (derivada) | +0,979 | 0,021 |

La `M` de la base `d2` se deriva del GL publicado despejando la identidad GL = 1 − |IBCR|, y queda
marcada como valor derivado en el diccionario de datos. Ambas bases sostienen la misma lectura de
negocio: Colombia es exportador neto y su comercio de este producto es interindustrial, de una sola vía.

## 6. Trazabilidad y reproducibilidad

Todo el procesamiento está escrito en Python con pandas (McKinney, 2022). Cada indicador de la carpeta
`04_indicadores_reales/` se regenera ejecutando `07_scripts/02_calcular_indicadores.py` sobre el archivo
crudo, sin edición manual de celdas. El script `03_validar_paquete.py` vuelve a verificar las identidades
matemáticas y escribe el resultado en `08_salidas/reporte_validacion.txt`.
