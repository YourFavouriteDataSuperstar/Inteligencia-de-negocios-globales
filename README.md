# Inteligencia de Negocios Globales

Material didáctico para aprender las **métricas de comercio exterior** con Python, a partir de un caso real y de datos oficiales sin limpiar.

**Universidad EAN** — Inteligencia en Negocios Globales — Semanas 4 y 5, niveles básico e intermedio.

---

## El caso

Una empresa floricultora colombiana exporta **claveles frescos** (partida arancelaria **HS 060312**). Hoy depende de **Estados Unidos** y quiere diversificar. El candidato sobre la mesa es **Corea del Sur**.

> ¿Corea del Sur es un buen destino, comparado con los cinco países que más claveles importan en el mundo?

Los cuadernos 1 y 2 responden esa pregunta con las métricas básicas. Los cuadernos 3 y 4 la vuelven a hacer con métricas de estructura y competitividad — y descubren, por el camino, que **la premisa del caso era falsa**: Corea del Sur no es un mercado por conquistar, es un mercado que Colombia ya domina con el 86,65 %.

---

## Cuadernos

| | Cuaderno | Qué aprendes | Abrir |
|---|---|---|---|
| 1 | **Fundamentos y preparación de datos** | Colab, Python, pandas y limpieza de datos oficiales | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YourFavouriteDataSuperstar/Inteligencia-de-negocios-globales/blob/main/notebooks/01_Fundamentos_y_preparacion_de_datos.ipynb) |
| 2 | **Métricas básicas de comercio exterior** | Balanza comercial e IBCR, Apertura Comercial y Coeficiente de Exportación | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YourFavouriteDataSuperstar/Inteligencia-de-negocios-globales/blob/main/notebooks/02_Metricas_basicas_de_comercio_exterior.ipynb) |
| 3 | **Concentración y estructura del comercio** | HHI, índice de Theil con su descomposición y Grubel-Lloyd | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YourFavouriteDataSuperstar/Inteligencia-de-negocios-globales/blob/main/notebooks/03_Concentracion_y_estructura_del_comercio.ipynb) |
| 4 | **Ventaja comparativa revelada** | La familia completa: Balassa, Laursen, Vollrath, NRCA y Lafay | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YourFavouriteDataSuperstar/Inteligencia-de-negocios-globales/blob/main/notebooks/04_Ventaja_comparativa_revelada.ipynb) |

### Cómo trabajarlos

**Cuadernos 1, 3 y 4.** Haz clic en el botón y ejecuta las celdas en orden. Vienen configurados en modo `"github"`: descargan sus propios datos de este repositorio. No tienes que subir nada.

**Cuaderno 2.** Necesita los tres archivos limpios que genera el Cuaderno 1, así que **ejecuta primero el Cuaderno 1**. Cuando abras el segundo, la celda de configuración te pedirá subirlos. Es a propósito: en un proyecto real primero se prepara el dato y después se calcula.

Los cuadernos 3 y 4 son independientes entre sí y de los anteriores: puedes abrir cualquiera de los dos directamente.

## Estructura del repositorio

```
.
├── notebooks/
│   ├── 01_Fundamentos_y_preparacion_de_datos.ipynb
│   ├── 02_Metricas_basicas_de_comercio_exterior.ipynb
│   ├── 03_Concentracion_y_estructura_del_comercio.ipynb
│   └── 04_Ventaja_comparativa_revelada.ipynb
└── data/
    │
    │  Cuadernos 1 y 2 — el producto del caso
    ├── importing-countries-in-2025_060312.csv          Trade Map: importaciones mundiales de HS 060312
    ├── exporting-countries-in-2025_060312.csv          Trade Map: exportaciones mundiales de HS 060312
    ├── API_NY.GDP.MKTP.CD_DS2_en_csv_v2_234.csv        Banco Mundial: PIB (USD corrientes)
    ├── API_NE.EXP.GNFS.CD_DS2_en_csv_v2_35140.csv      Banco Mundial: exportaciones totales
    ├── API_NE.IMP.GNFS.CD_DS2_en_csv_v2_33330.csv      Banco Mundial: importaciones totales
    ├── Metadata_Country_API_NY.GDP.MKTP.CD_...csv      Banco Mundial: región y grupo de ingreso por país
    ├── Metadata_Indicator_API_NY.GDP.MKTP.CD_...csv    Banco Mundial: definición del indicador
    │
    │  Cuadernos 3 y 4 — la canasta exportadora completa
    ├── co_exp_productos_hs2_serie.xls                  Trade Map: Colombia exporta, 97 capítulos HS, 2021-2025
    ├── co_imp_productos_hs2_serie.csv                  Trade Map: Colombia importa, 97 capítulos HS, 2021-2025
    ├── mundo_exp_productos_hs2_serie.csv               Trade Map: el mundo exporta, 97 capítulos HS
    ├── mundo_imp_productos_hs2_serie.csv               Trade Map: el mundo importa, 97 capítulos HS
    ├── co_exp_productos_hs2_indicadores.xls            Trade Map: vista de indicadores, con concentración de destinos
    ├── co_060312_destinos_indicadores.csv              Trade Map: a quién le vende Colombia claveles
    ├── co_060312_destinos_serie.csv                    Trade Map: lo mismo, serie 2016-2025
    ├── kor_060312_proveedores_indicadores.csv          Trade Map: quién le vende claveles a Corea del Sur
    ├── kor_060312_proveedores_serie.csv                Trade Map: lo mismo, serie 2016-2025
    ├── co_060312_destinos_legiscomex.csv               DIAN vía Legiscomex: destinos por año, agregado
    └── co_060312_auditoria_descargas_legiscomex.csv    Auditoría de las siete descargas de Legiscomex
```

### Sobre los datos

Los archivos de `data/` están **sin limpiar**, exactamente como se descargaron de la fuente. Eso es intencional: limpiarlos es el ejercicio del Cuaderno 1.

Entre otras cosas, vas a encontrarte con códigos de país que pierden el cero inicial, totales mundiales disfrazados de países, valores en miles de dólares mezclados con valores en dólares, unidades de cantidad incompatibles entre países, cuatro líneas de metadatos antes del encabezado, formato ancho con un año por columna, agregados regionales revueltos con países y dos sistemas de codificación de país que no se entienden entre sí.

Y en los archivos de los cuadernos 3 y 4, cuatro trampas nuevas: **archivos `.xls` que en realidad son HTML**, códigos de capítulo con un apóstrofe pegado delante, miles separados por coma que llegan como texto, y una fila de navegación de la página web antes del encabezado real.

**Sobre los datos de Legiscomex.** Legiscomex es una base por suscripción. Aquí solo se redistribuye la **tabla agregada por país de destino** —un dato derivado, no el extracto transaccional— junto con la auditoría de las descargas. El detalle declaración por declaración (273.033 registros) no se publica. La fuente primaria es la DIAN.

---

## Qué se calcula

| Cuaderno | Métrica | Pregunta que responde | Rango |
|---|---|---|---|
| 2 | **Balanza Comercial e IBCR** | ¿Este país produce lo que consume, o depende de comprarlo afuera? | de −1 a +1 |
| 2 | **Índice de Apertura Comercial** | ¿Qué tan atada al comercio internacional está esta economía? | porcentaje, sin techo |
| 2 | **Coeficiente de Exportación** | De todo lo que producimos, ¿cuánto se va al exterior? | 0 % a 100 % |
| 3 | **Herfindahl-Hirschman (HHI)** | ¿De cuántos clientes —o productos— depende realmente este negocio? | de 0 a 1 |
| 3 | **Índice de Theil** | ¿La diversificación que veo es estructural o es apariencia? | de 0 a ∞, descomponible |
| 3 | **Grubel-Lloyd** | ¿Esto es competencia real o intercambio dentro de una misma cadena? | de 0 a 1 |
| 4 | **Balassa (RCA)** | ¿Exporto proporcionalmente más de esto que el resto del mundo? | de 0 a ∞ |
| 4 | **Laursen (RSCA)** | Lo mismo, pero en una escala que sirve para regresiones | de −1 a +1 |
| 4 | **Vollrath (RXA, RMA, RTA, RC)** | ¿La ventaja es producción propia o ensamblaje de insumos importados? | simétrico en 0 |
| 4 | **NRCA (Yu, Cai y Leung)** | ¿Cuánto se desvía el país de su punto neutral? | simétrico, suma cero |
| 4 | **Lafay (LFI)** | ¿Este producto va mejor que el promedio comercial del propio país? | suma cero |

Cada métrica se presenta con la misma estructura: qué es, para qué sirve, la fórmula explicada término por término, un ejemplo numérico paso a paso, el cálculo sobre datos reales, la interpretación con sus umbrales, el impacto en el negocio y de dónde sale exactamente el dato.

---

## Requisitos

Ninguno más allá de una cuenta de Google. Los cuadernos corren en Google Colab con las bibliotecas que ya vienen instaladas: `pandas`, `numpy` y `matplotlib`.

Si prefieres correrlos en tu computador, necesitas Python 3.9 o superior con esas tres bibliotecas, y cambiar `MODO` a `"local"` en la celda de configuración.

---

## Fuentes de datos

- **Trade Map** — International Trade Centre. https://www.trademap.org
- **World Development Indicators** — Banco Mundial. https://data.worldbank.org
- **Legiscomex** — Sistema de Inteligencia Comercial (acceso institucional Universidad EAN). Datos primarios de la **DIAN**. https://www.legiscomex.com

Los datos son de acceso público. Se redistribuyen aquí con fines exclusivamente educativos, conservando su forma original y citando la fuente.

---

## Referencias

Baena-Rojas, J. J., & Cano, J. A. (2026). International market selection for exports of goods: A data analysis technique for organizational decision-making. *Global Business Review*. https://doi.org/10.1177/09721509261464305

Balassa, B. (1965). Trade liberalisation and "revealed" comparative advantage. *The Manchester School, 33*(2), 99–123.

Durán Lima, J. E. (s.f.). *Indicadores de comercio exterior y política comercial: Generalidades metodológicas e indicadores básicos*. Comisión Económica para América Latina y el Caribe.

Grubel, H. G., & Lloyd, P. J. (1975). *Intra-industry trade: The theory and measurement of international trade in differentiated products*. Macmillan.

International Trade Centre. (2025). *Trade Map: Trade statistics for international business development*. https://www.trademap.org

McKinney, W. (2010). Data structures for statistical computing in Python. En S. van der Walt & J. Millman (Eds.), *Proceedings of the 9th Python in Science Conference* (pp. 56–61). https://doi.org/10.25080/Majora-92bf1922-00a

Vollrath, T. L. (1991). A theoretical evaluation of alternative trade intensity measures of revealed comparative advantage. *Weltwirtschaftliches Archiv, 127*(2), 265–280.

World Bank. (2025). *World Development Indicators*. https://data.worldbank.org

Yu, R., Cai, J., & Leung, P. (2009). The normalized revealed comparative advantage index. *The Annals of Regional Science, 43*(1), 267–282.

La lista completa de referencias en formato APA 7, incluyendo la documentación de todas las bibliotecas utilizadas, está al final de cada cuaderno.
