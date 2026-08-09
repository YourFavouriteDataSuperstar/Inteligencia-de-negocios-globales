# Inteligencia de Negocios Globales

Material didáctico para aprender las **métricas básicas de comercio exterior** con Python, a partir de un caso real y de datos oficiales sin limpiar.

**Universidad EAN** — Inteligencia en Negocios Globales — Semana 4, nivel básico.

---

## El caso

Una empresa floricultora colombiana exporta **claveles frescos** (partida arancelaria **HS 060312**). Hoy depende de **Estados Unidos** y quiere diversificar. El candidato sobre la mesa es **Corea del Sur**.

> ¿Corea del Sur es un buen destino, comparado con los cinco países que más claveles importan en el mundo?

Para responder hay que hacer dos cosas, en este orden: preparar los datos y calcular las métricas. Un cuaderno para cada una.

---

## Cuadernos

| | Cuaderno | Qué aprendes | Abrir |
|---|---|---|---|
| 1 | **Fundamentos y preparación de datos** | Colab, Python, pandas y limpieza de datos oficiales | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YourFavouriteDataSuperstar/Inteligencia-de-negocios-globales/blob/main/notebooks/01_Fundamentos_y_preparacion_de_datos.ipynb) |
| 2 | **Métricas básicas de comercio exterior** | Balanza comercial e IBCR, Apertura Comercial y Coeficiente de Exportación | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YourFavouriteDataSuperstar/Inteligencia-de-negocios-globales/blob/main/notebooks/02_Metricas_basicas_de_comercio_exterior.ipynb) |

### Cómo trabajarlos

**Cuaderno 1.** Haz clic en el botón, ejecuta las celdas en orden y listo: viene configurado en modo `"github"`, así que descarga los datos de este repositorio solo. No tienes que subir nada.

Al final genera tres archivos limpios y los descarga a tu computador:

- `comercio_060312_limpio.csv`
- `macro_paises_limpio.csv`
- `tablero_caso_limpio.csv`

**Cuaderno 2.** Necesita esos tres archivos, así que **ejecuta primero el Cuaderno 1**. Cuando abras el segundo, la celda de configuración te pedirá subirlos. Es a propósito: en un proyecto real primero se prepara el dato y después se calcula.

---

## Estructura del repositorio

```
.
├── notebooks/
│   ├── 01_Fundamentos_y_preparacion_de_datos.ipynb
│   └── 02_Metricas_basicas_de_comercio_exterior.ipynb
└── data/
    ├── importing-countries-in-2025_060312.csv          Trade Map: importaciones mundiales de HS 060312
    ├── exporting-countries-in-2025_060312.csv          Trade Map: exportaciones mundiales de HS 060312
    ├── API_NY.GDP.MKTP.CD_DS2_en_csv_v2_234.csv        Banco Mundial: PIB (USD corrientes)
    ├── API_NE.EXP.GNFS.CD_DS2_en_csv_v2_35140.csv      Banco Mundial: exportaciones totales
    ├── API_NE.IMP.GNFS.CD_DS2_en_csv_v2_33330.csv      Banco Mundial: importaciones totales
    ├── Metadata_Country_API_NY.GDP.MKTP.CD_...csv      Banco Mundial: región y grupo de ingreso por país
    └── Metadata_Indicator_API_NY.GDP.MKTP.CD_...csv    Banco Mundial: definición del indicador
```

### Sobre los datos

Los archivos de `data/` están **sin limpiar**, exactamente como se descargaron de la fuente. Eso es intencional: limpiarlos es el ejercicio del Cuaderno 1.

Entre otras cosas, vas a encontrarte con códigos de país que pierden el cero inicial, totales mundiales disfrazados de países, valores en miles de dólares mezclados con valores en dólares, unidades de cantidad incompatibles entre países, cuatro líneas de metadatos antes del encabezado, formato ancho con un año por columna, agregados regionales revueltos con países y dos sistemas de codificación de país que no se entienden entre sí.

---

## Qué se calcula

| Métrica | Pregunta que responde | Rango |
|---|---|---|
| **Balanza Comercial e IBCR** | ¿Este país produce lo que consume, o depende de comprarlo afuera? | de −1 a +1 |
| **Índice de Apertura Comercial** | ¿Qué tan atada al comercio internacional está esta economía? | porcentaje, sin techo fijo |
| **Coeficiente de Exportación** | De todo lo que producimos, ¿cuánto se va al exterior? | 0 % a 100 % |

Cada métrica se presenta con la misma estructura: qué es, para qué sirve, la fórmula explicada término por término, un ejemplo numérico paso a paso, el cálculo sobre datos reales, la interpretación con sus umbrales, el impacto en el negocio y de dónde sale exactamente el dato.

---

## Requisitos

Ninguno más allá de una cuenta de Google. Los cuadernos corren en Google Colab con las bibliotecas que ya vienen instaladas: `pandas`, `numpy` y `matplotlib`.

Si prefieres correrlos en tu computador, necesitas Python 3.9 o superior con esas tres bibliotecas, y cambiar `MODO` a `"local"` en la celda de configuración.

---

## Fuentes de datos

- **Trade Map** — International Trade Centre. https://www.trademap.org
- **World Development Indicators** — Banco Mundial. https://data.worldbank.org

Los datos son de acceso público. Se redistribuyen aquí con fines exclusivamente educativos, conservando su forma original y citando la fuente.

---

## Referencias

Baena-Rojas, J. J., & Cano, J. A. (2026). International market selection for exports of goods: A data analysis technique for organizational decision-making. *Global Business Review*. https://doi.org/10.1177/09721509261464305

Durán Lima, J. E. (s.f.). *Indicadores de comercio exterior y política comercial: Generalidades metodológicas e indicadores básicos*. Comisión Económica para América Latina y el Caribe.

International Trade Centre. (2025). *Trade Map: Trade statistics for international business development*. https://www.trademap.org

McKinney, W. (2010). Data structures for statistical computing in Python. En S. van der Walt & J. Millman (Eds.), *Proceedings of the 9th Python in Science Conference* (pp. 56–61). https://doi.org/10.25080/Majora-92bf1922-00a

World Bank. (2025). *World Development Indicators*. https://data.worldbank.org

La lista completa de referencias en formato APA 7, incluyendo la documentación de todas las bibliotecas utilizadas, está al final de cada cuaderno.
