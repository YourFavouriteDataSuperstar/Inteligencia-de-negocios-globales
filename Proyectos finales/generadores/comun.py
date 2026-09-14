"""Piezas comunes para generar los cuadernos de los proyectos finales."""
import os
import nbformat as nbf

REPO = "YourFavouriteDataSuperstar/Inteligencia-de-negocios-globales"
COLAB = f"https://colab.research.google.com/github/{REPO}/blob/main/"
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # raiz del repositorio


def md(texto):
    return nbf.v4.new_markdown_cell(texto.strip("\n"))


def code(texto):
    return nbf.v4.new_code_cell(texto.strip("\n"))


def analisis(pregunta=""):
    guia = f" {pregunta}" if pregunta else ""
    return md(
        f"**Análisis del equipo:**{guia}\n\n_(Escriban aquí qué muestra la gráfica, "
        "qué significa para el caso y qué decisión habilita. Borren esta línea al terminar.)_"
    )


def badge(ruta_nb):
    url = COLAB + ruta_nb.replace(" ", "%20")
    return md(
        f'<a href="{url}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir en Colab"/></a>'
    )


def portada(titulo, grupo, producto, pregunta, metricas, ficha):
    filas = "\n".join(f"| **{m}** | {q} |" for m, q in metricas)
    return md(f"""
# {titulo}

**Asignatura:** Inteligencia en Negocios Globales — Universidad EAN
**Proyecto final — {grupo}**
**Producto:** {producto}
**Ficha técnica de referencia:** {ficha}

---

## La pregunta del equipo

> {pregunta}

## Lo que calcula este cuaderno

Cada sección corresponde a un análisis que el equipo propuso en su ficha técnica. El cuaderno **calcula y grafica; no interpreta**. La interpretación es el trabajo del equipo.

| Métrica o análisis | Pregunta que responde |
|---|---|
{filas}

## Cómo usar este cuaderno

1. Ejecuta las celdas **en orden**, de arriba hacia abajo (`Entorno de ejecución → Ejecutar todas`). Viene en modo `"github"`: descarga sus propios datos del repositorio del curso, no tienes que subir nada.
2. Después de cada gráfica hay una celda que dice **Análisis del equipo**. Haz doble clic sobre ella y escribe la interpretación. Puedes agregar más celdas de texto donde quieras.
3. Las celdas marcadas **editable** contienen pesos o puntajes que el equipo debe ajustar con su propio criterio. Cámbialos y vuelve a ejecutar.
4. Al terminar: `Archivo → Descargar → Descargar .ipynb` y sube el archivo al aula virtual.

Todas las tablas y figuras se guardan además en la carpeta `salidas/` (panel izquierdo de Colab) para que las uses en el informe.
""")


CELL_IMPORTS = code('''
import os
import io
import csv
import glob
import time
import shutil
import zipfile
import urllib.request
import urllib.error
import urllib.parse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.float_format", lambda x: f"{x:,.4f}")
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 170)

# Paleta de colores del curso (validada para lectura accesible en pantalla e impresion)
AZUL      = "#2a78d6"    # serie principal / pais del caso
ROJO      = "#e34948"    # valores negativos (par divergente con el azul)
NARANJA   = "#eb6834"    # elemento destacado
VERDE     = "#3f8f6b"    # segunda serie categorica
GRIS_MID  = "#c3c2b7"    # resto / punto neutro
TINTA     = "#0b0b0b"
GRIS_TEXT = "#52514e"
GRIS_EJE  = "#898781"
REJILLA   = "#e1e0d9"

# Orden fijo de colores para series categoricas: nunca se reciclan, lo que sobra va a "Otros" en gris
CATEGORIAS = [AZUL, NARANJA, VERDE, ROJO]

CARPETA_SALIDA = "salidas"
os.makedirs(CARPETA_SALIDA, exist_ok=True)


def estilo(ax, titulo, subtitulo="", fuente="", eje_y="", eje_x="", rejilla="y"):
    """Aplica el estilo de graficas del curso: titulo a la izquierda, sin marco, rejilla suave, fuente al pie."""
    ax.set_title(titulo + ("\\n" + subtitulo if subtitulo else ""),
                 fontsize=13, color=TINTA, loc="left", pad=14)
    ax.set_ylabel(eje_y, fontsize=10, color=GRIS_TEXT)
    ax.set_xlabel(eje_x, fontsize=10, color=GRIS_TEXT)
    if rejilla == "y":
        ax.yaxis.grid(True, color=REJILLA, linewidth=0.8)
    elif rejilla == "x":
        ax.xaxis.grid(True, color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRIS_EJE)
    ax.tick_params(colors=GRIS_EJE, labelsize=9)
    if fuente:
        ax.figure.text(0.01, -0.03, "Fuente: " + fuente, fontsize=8, color=GRIS_EJE, ha="left")


def guardar(fig, nombre):
    """Muestra la figura y la guarda como PNG en la carpeta de salidas."""
    ruta = os.path.join(CARPETA_SALIDA, nombre + ".png")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.show()
    print("Figura guardada en", ruta)


def exportar(tabla, nombre):
    """Guarda una tabla como CSV en la carpeta de salidas y la devuelve para mostrarla."""
    tabla.to_csv(os.path.join(CARPETA_SALIDA, nombre + ".csv"), index=False, encoding="utf-8-sig")
    return tabla


def fmt_miles(x, _=None):
    """Formato de eje para valores en miles de USD: 1200 -> 1.2 mn ; 850 -> 850 k."""
    if abs(x) >= 1_000_000:
        return f"{x / 1_000_000:.1f} mil mn"
    if abs(x) >= 1_000:
        return f"{x / 1_000:.1f} mn"
    return f"{x:.0f} k"


def fmt_unidades(x, _=None):
    """Formato de eje para valores en unidades: 1.5e9 -> 1.5 mil mn ; 2.4e6 -> 2.4 mn ; 850000 -> 850 k."""
    if abs(x) >= 1e9:
        return f"{x / 1e9:.1f} mil mn"
    if abs(x) >= 1e6:
        return f"{x / 1e6:.1f} mn"
    if abs(x) >= 1e3:
        return f"{x / 1e3:.0f} k"
    return f"{x:.0f}"


def leyenda_fuera(ax):
    """Leyenda a la derecha del grafico, para que no tape barras ni la nota de fuente."""
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1.01, 1))


print("pandas:", pd.__version__, "| numpy:", np.__version__)
''')


def cell_config(grupo_dir, archivos, extra=""):
    lineas = "\n".join(f'    "{k}": "{v}",' for k, v in archivos.items())
    return code(f'''
# ============================================================
#  CONFIGURACION: cambia solo esta celda si lo necesitas
# ============================================================

MODO = "github"         # opciones: "github" | "subir" | "local"

REPO_CURSO = "{REPO}"
RAMA = "main"

# Archivos que necesita este cuaderno, con su ruta dentro del repositorio del curso.
# Los del grupo estan en "{grupo_dir}/datos/"; los demas son datos del curso en "data/".
ARCHIVOS_REPO = {{
{lineas}
}}

RUTA_LOCAL = "../.."    # solo si MODO = "local": raiz del repositorio, corriendo desde la carpeta del grupo
{extra}
print(f"Modo seleccionado: {{MODO}}  |  {{len(ARCHIVOS_REPO)}} archivos")
''')


CELL_DESCARGA = code('''
# ============================================================
#  Ejecuta esta celda tal cual: consigue los datos segun el modo
# ============================================================

def pedir(url, intentos=5):
    """Descarga una URL, reintentando si el servidor pide esperar (HTTP 429 de GitHub en Colab)."""
    for intento in range(intentos):
        try:
            peticion = urllib.request.Request(url, headers={"User-Agent": "cuaderno-ean"})
            with urllib.request.urlopen(peticion, timeout=90) as respuesta:
                return respuesta.read()
        except urllib.error.HTTPError as error:
            if error.code not in (403, 429, 500, 502, 503) or intento == intentos - 1:
                raise
            espera = int(error.headers.get("Retry-After") or 0) or 2 ** intento
            print(f"    servidor ocupado (HTTP {error.code}); reintento en {espera} s")
            time.sleep(espera)
        except urllib.error.URLError:
            if intento == intentos - 1:
                raise
            time.sleep(2 ** intento)


def descargar_datos(rutas_repo, destino):
    """Trae los archivos del repositorio a la carpeta destino, en una sola peticion (zip del repo).

    Cada archivo se guarda por su nombre, sin carpetas. Si ya existe no se vuelve a bajar.
    Si el zip falla, baja los archivos uno por uno desde raw.githubusercontent.com.
    """
    os.makedirs(destino, exist_ok=True)
    faltan = [r for r in rutas_repo if not os.path.exists(os.path.join(destino, os.path.basename(r)))]
    if not faltan:
        print(f"Los {len(rutas_repo)} archivos ya estaban descargados.")
        return
    try:
        print(f"Descargando {len(faltan)} archivos en una sola peticion...\\n")
        comprimido = pedir(f"https://codeload.github.com/{REPO_CURSO}/zip/refs/heads/{RAMA}")
        with zipfile.ZipFile(io.BytesIO(comprimido)) as paquete:
            for miembro in paquete.namelist():
                relativo = miembro.split("/", 1)[1] if "/" in miembro else miembro
                if relativo in faltan:
                    with paquete.open(miembro) as origen, \\
                         open(os.path.join(destino, os.path.basename(relativo)), "wb") as salida:
                        shutil.copyfileobj(origen, salida)
                    print(f"  extraido: {os.path.basename(relativo)}")
    except Exception as error:
        print(f"\\n  El paquete fallo ({type(error).__name__}). Voy archivo por archivo.\\n")
        for relativo in faltan:
            url = f"https://raw.githubusercontent.com/{REPO_CURSO}/{RAMA}/" + urllib.parse.quote(relativo)
            with open(os.path.join(destino, os.path.basename(relativo)), "wb") as salida:
                salida.write(pedir(url))
            print(f"  descargado: {os.path.basename(relativo)}")
            time.sleep(0.5)
    perdidos = [r for r in rutas_repo if not os.path.exists(os.path.join(destino, os.path.basename(r)))]
    if perdidos:
        raise FileNotFoundError(f"No se pudieron descargar: {perdidos}. Espera un minuto y vuelve a ejecutar.")


if MODO == "github":
    RUTA_BASE = "datos_crudos"
    descargar_datos(list(ARCHIVOS_REPO.values()), RUTA_BASE)

    def ruta(clave):
        return os.path.join(RUTA_BASE, os.path.basename(ARCHIVOS_REPO[clave]))

elif MODO == "subir":
    from google.colab import files
    print("Sube estos archivos:\\n  " + "\\n  ".join(os.path.basename(v) for v in ARCHIVOS_REPO.values()))
    files.upload()
    RUTA_BASE = "/content"

    def ruta(clave):
        encontrados = glob.glob(os.path.join(RUTA_BASE, "**", os.path.basename(ARCHIVOS_REPO[clave])), recursive=True)
        if not encontrados:
            raise FileNotFoundError(f"Falta el archivo {os.path.basename(ARCHIVOS_REPO[clave])}")
        return encontrados[0]

else:  # local
    RUTA_BASE = RUTA_LOCAL

    def ruta(clave):
        return os.path.join(RUTA_BASE, ARCHIVOS_REPO[clave])

for clave in ARCHIVOS_REPO:
    estado = "ok" if os.path.exists(ruta(clave)) else "FALTA"
    print(f"  {estado:5s} {clave:14s} -> {os.path.basename(ARCHIVOS_REPO[clave])}")
''')


CELL_LECTORES = code('''
# ============================================================
#  Lectores: cada funcion resuelve las trampas de un tipo de archivo
# ============================================================

def a_numero(serie):
    """Convierte a numero una columna que viene como texto (miles con coma, simbolos, espacios)."""
    return pd.to_numeric(
        pd.Series(serie).astype(str)
                        .str.replace(",", "", regex=False)
                        .str.replace(r"[^0-9.\\-]", "", regex=True)
                        .replace("", np.nan),
        errors="coerce",
    )


# Nombres cortos en espanol para las columnas de Trade Map
COLUMNAS_TM = {
    "Value (kUSD)": "valor_kusd",
    "Balance (kUSD)": "balanza_kusd",
    "Quantity": "cantidad",
    "Quantity Unit": "unidad_cantidad",
    "Unit Value": "valor_unitario",
    "Unit Value Unit": "unidad_valor_unitario",
    "Share (%)": "participacion_pct",
    "Share Partner Country (%)": "cuota_en_socio_pct",
    "Share World (%)": "participacion_mundial_pct",
    "Ranking Partners": "ranking_socio",
    "Growth Value 5Y (%)": "crec_valor_5a_pct",
    "Growth Value 2Y (%)": "crec_valor_2a_pct",
    "Growth Value Partners 5Y (%)": "crec_importaciones_socio_5a_pct",
    "Growth Quantity 5Y (%)": "crec_cantidad_5a_pct",
}

AGREGADOS_NO_PAIS = ["Zona franca", "Zonas francas", "Áreas Nes", "Areas, nes", "Zona Nep", "Free Zones"]


def leer_trademap(ruta_archivo):
    """Lee una tabla de indicadores de Trade Map (corte de un anio, formato largo).

    Trampas que resuelve: una columna sin nombre en el encabezado, codigos de pais con cero
    inicial que pandas convertiria a entero, valor unitario con 28 decimales, y la fila
    "Mundo" mezclada con los paises. La columna `pais` queda lista para usar.
    """
    tabla = pd.read_csv(ruta_archivo, dtype={"reporterCd": str, "partnerCd": str, "productCd": str},
                        encoding="utf-8-sig")
    return limpiar_trademap(tabla)


def limpiar_trademap(tabla):
    """Limpieza comun a toda tabla de indicadores de Trade Map, venga de CSV o de Excel."""
    tabla = tabla.loc[:, ~tabla.columns.str.startswith("Unnamed")]
    for columna in ("reporterCd", "partnerCd"):
        tabla[columna] = tabla[columna].astype(str).str.replace(r"\\.0$", "", regex=True).str.zfill(3)
    tabla = tabla.rename(columns=COLUMNAS_TM)
    for columna in COLUMNAS_TM.values():
        if columna in tabla.columns and columna not in ("unidad_cantidad", "unidad_valor_unitario"):
            tabla[columna] = a_numero(tabla[columna])
    if "valor_unitario" in tabla.columns:
        tabla["valor_unitario"] = tabla["valor_unitario"].round(2)
    # Si todos los socios son "Mundo", la tabla es una lista de paises (reporter); si no, es una lista de socios
    if (tabla["partnerCd"] == "000").all():
        tabla["codigo"], tabla["pais"] = tabla["reporterCd"], tabla["reporterLabel"]
    else:
        tabla["codigo"], tabla["pais"] = tabla["partnerCd"], tabla["partnerLabel"]
    return tabla


def separar_mundo(tabla):
    """Devuelve (fila Mundo, tabla solo con paises). Excluye agregados que no son paises."""
    es_mundo = tabla["codigo"] == "000"
    mundo = tabla[es_mundo].iloc[0]
    paises = tabla[~es_mundo & ~tabla["pais"].isin(AGREGADOS_NO_PAIS)].reset_index(drop=True)
    return mundo, paises


def leer_serie_trademap(ruta_archivo):
    """Lee la serie anual por socio (un anio por columna) y la devuelve en formato largo.

    Columnas de salida: codigo, pais, anio, valor_kusd. Incluye la fila Mundo (codigo 000).
    """
    tabla = pd.read_csv(ruta_archivo, dtype=str, encoding="utf-8-sig")
    columnas_anio = [c for c in tabla.columns if c[:4].isdigit()]
    tabla = tabla.rename(columns={c: c[:4] for c in columnas_anio})
    anios = [c[:4] for c in columnas_anio]
    for anio in anios:
        tabla[anio] = a_numero(tabla[anio])
    if (tabla["partnerCd"] == "000").all():
        tabla["codigo"], tabla["pais"] = tabla["reporterCd"], tabla["reporterLabel"]
    else:
        tabla["codigo"], tabla["pais"] = tabla["partnerCd"], tabla["partnerLabel"]
    largo = tabla.melt(id_vars=["codigo", "pais"], value_vars=anios, var_name="anio", value_name="valor_kusd")
    largo["anio"] = largo["anio"].astype(int)
    return largo.sort_values(["anio", "valor_kusd"], ascending=[True, False]).reset_index(drop=True)


def leer_banco_mundial(ruta_archivo, nombre_indicador):
    """Lee un archivo del Banco Mundial: cuatro filas de metadatos antes del encabezado y un anio por columna."""
    tabla = pd.read_csv(ruta_archivo, skiprows=4, encoding="utf-8-sig")
    tabla = tabla.loc[:, ~tabla.columns.str.startswith("Unnamed")]
    anios = [c for c in tabla.columns if c.isdigit()]
    largo = tabla.melt(id_vars=["Country Name", "Country Code"], value_vars=anios,
                       var_name="anio", value_name=nombre_indicador)
    largo["anio"] = largo["anio"].astype(int)
    return largo.rename(columns={"Country Name": "pais", "Country Code": "iso3"})


ANIOS_CANASTA = [str(a) for a in range(2021, 2026)]


def leer_canasta(ruta_archivo):
    """Lee la canasta por capitulo HS del curso (97 capitulos + TOTAL, 2021-2025).

    Funciona igual si el archivo es un .csv o un .xls que en realidad es HTML.
    Trampas: apostrofe delante del codigo y miles separados por coma como texto.
    """
    with open(ruta_archivo, encoding="utf-8", errors="ignore") as f:
        primeras_letras = f.read(200).lstrip().lower()
    if primeras_letras.startswith("<"):
        tabla = max(pd.read_html(ruta_archivo), key=lambda t: t.shape[0])
    else:
        tabla = pd.read_csv(ruta_archivo)
    tabla = tabla.iloc[:, -7:]
    tabla.columns = ["codigo", "producto"] + ANIOS_CANASTA
    tabla["codigo"] = tabla["codigo"].astype(str).str.strip().str.lstrip("'").str.strip()
    for anio in ANIOS_CANASTA:
        tabla[anio] = a_numero(tabla[anio])
    return tabla.dropna(subset=["2025"]).reset_index(drop=True)


def fila_canasta(canasta, codigo):
    """Devuelve la serie 2021-2025 (en USD miles) de un codigo de la canasta: un capitulo HS2 o "TOTAL"."""
    fila = canasta[canasta["codigo"] == codigo]
    if fila.empty:
        raise KeyError(f"No encontre el codigo {codigo} en la canasta")
    return fila.iloc[0][ANIOS_CANASTA].astype(float)


print("Lectores listos.")
''')


# --- Funciones de metricas, tomadas de los cuadernos 2, 3 y 4 del curso ---
METRICAS = {
    "hhi": '''
def hhi(valores):
    """Indice de Herfindahl-Hirschman: suma de participaciones al cuadrado. Entre 0 y 1."""
    valores = np.asarray(valores, dtype=float)
    valores = valores[~np.isnan(valores)]
    valores = valores[valores > 0]
    if valores.sum() == 0:
        return np.nan
    participaciones = valores / valores.sum()
    return float(np.sum(participaciones ** 2))


def numeros_equivalentes(indice_hhi):
    """Cuantos destinos del mismo tamano equivaldrian a esta reparticion: 1 / HHI."""
    return 1 / indice_hhi
''',
    "cr": '''
def cr_n(valores, n):
    """Razon de concentracion CR_n: participacion conjunta (%) de los n mayores."""
    valores = np.sort(np.asarray(valores, dtype=float))[::-1]
    valores = valores[~np.isnan(valores)]
    return float(valores[:n].sum() / valores.sum() * 100)
''',
    "theil": '''
def theil(valores):
    """Indice de Theil: dispersion por entropia. 0 = reparto perfectamente igual; sin techo superior."""
    valores = np.asarray(valores, dtype=float)
    valores = valores[valores > 0]
    n = len(valores)
    media = valores.mean()
    return float((1 / n) * np.sum((valores / media) * np.log(valores / media)))
''',
    "gl": '''
def grubel_lloyd(exportaciones, importaciones):
    """Indice de Grubel-Lloyd: 1 = comercio intraindustrial puro, 0 = interindustrial puro."""
    exportaciones = np.asarray(exportaciones, dtype=float)
    importaciones = np.asarray(importaciones, dtype=float)
    comercio_total = exportaciones + importaciones
    return np.where(comercio_total > 0, 1 - np.abs(exportaciones - importaciones) / comercio_total, np.nan)
''',
    "ibcr": '''
def ibcr(exportaciones, importaciones):
    """Indice de Balanza Comercial Relativa: (X - M) / (X + M), entre -1 y +1."""
    exportaciones = np.asarray(exportaciones, dtype=float)
    importaciones = np.asarray(importaciones, dtype=float)
    comercio_total = exportaciones + importaciones
    return np.where(comercio_total > 0, (exportaciones - importaciones) / comercio_total, np.nan)
''',
    "apertura": '''
def apertura_comercial(exportaciones_totales, importaciones_totales, pib):
    """Indice de Apertura Comercial: (X + M) / PIB x 100, con los flujos TOTALES de la economia."""
    pib = np.asarray(pib, dtype=float)
    return np.where(pib > 0, (np.asarray(exportaciones_totales, dtype=float) + np.asarray(importaciones_totales, dtype=float)) / pib * 100, np.nan)
''',
    "ce": '''
def coeficiente_exportacion(exportaciones, valor_produccion):
    """Coeficiente de Exportacion: X / produccion x 100."""
    valor_produccion = np.asarray(valor_produccion, dtype=float)
    return np.where(valor_produccion > 0, np.asarray(exportaciones, dtype=float) / valor_produccion * 100, np.nan)
''',
    "rca": '''
def rca_balassa(x_pais, x_pais_total, x_mundo, x_mundo_total):
    """Ventaja Comparativa Revelada de Balassa (1965). Mayor que 1 = especializacion revelada."""
    participacion_pais  = np.asarray(x_pais, dtype=float)  / np.asarray(x_pais_total, dtype=float)
    participacion_mundo = np.asarray(x_mundo, dtype=float) / np.asarray(x_mundo_total, dtype=float)
    return participacion_pais / participacion_mundo


def rsca_laursen(rca):
    """RCA simetrico de Laursen: (RCA - 1) / (RCA + 1), entre -1 y +1, con 0 como punto neutro."""
    rca = np.asarray(rca, dtype=float)
    return (rca - 1) / (rca + 1)
''',
    "nrca": '''
def nrca(x_pais, x_pais_total, x_mundo, x_mundo_total):
    """NRCA de Yu, Cai y Leung (2009): distancia entre la exportacion observada y la neutral. Suma cero."""
    x_pais, x_mundo = np.asarray(x_pais, dtype=float), np.asarray(x_mundo, dtype=float)
    x_pais_total, x_mundo_total = float(x_pais_total), float(x_mundo_total)
    observado = x_pais / x_mundo_total
    neutral   = (x_pais_total * x_mundo) / (x_mundo_total ** 2)
    return observado - neutral
''',
    "vollrath": '''
def indices_vollrath(x_pais, m_pais, x_mundo, m_mundo, xt_pais, mt_pais, xt_mundo, mt_mundo):
    """Familia de Vollrath (1991): RXA, RMA, RTA y RC. Los denominadores excluyen al propio pais y al propio producto."""
    x_pais, m_pais, x_mundo, m_mundo = (float(v) for v in (x_pais, m_pais, x_mundo, m_mundo))
    xt_pais, mt_pais, xt_mundo, mt_mundo = (float(v) for v in (xt_pais, mt_pais, xt_mundo, mt_mundo))
    rxa = (x_pais / (xt_pais - x_pais)) / ((x_mundo - x_pais) / ((xt_mundo - x_mundo) - (xt_pais - x_pais)))
    rma = (m_pais / (mt_pais - m_pais)) / ((m_mundo - m_pais) / ((mt_mundo - m_mundo) - (mt_pais - m_pais)))
    return {"RXA": rxa, "RMA": rma, "RTA": rxa - rma, "RC": np.log(rxa) - np.log(rma)}
''',
    "lafay": '''
def lafay(x_pais, m_pais):
    """Indice de Lafay (1992) sobre una canasta completa: positivo = el producto va mejor que el promedio del pais."""
    x_pais = np.asarray(x_pais, dtype=float)
    m_pais = np.asarray(m_pais, dtype=float)
    comercio_producto = x_pais + m_pais
    comercio_total    = comercio_producto.sum()
    ibcr_producto = np.where(comercio_producto > 0, (x_pais - m_pais) / comercio_producto, 0)
    ibcr_nacional = (x_pais - m_pais).sum() / comercio_total
    peso_producto = comercio_producto / comercio_total
    return 100 * (ibcr_producto - ibcr_nacional) * peso_producto
''',
    "cagr": '''
def cagr(valor_inicial, valor_final, anios):
    """Tasa de crecimiento anual compuesto (%) entre dos valores separados por `anios` anios."""
    valor_inicial, valor_final = float(valor_inicial), float(valor_final)
    if valor_inicial <= 0 or valor_final <= 0 or anios <= 0:
        return np.nan
    return ((valor_final / valor_inicial) ** (1 / anios) - 1) * 100
''',
    "multicriterio": '''
def matriz_multicriterio(puntajes, pesos):
    """Pondera una tabla de puntajes (filas = criterios, columnas = mercados) con un diccionario de pesos.

    Devuelve la contribucion de cada criterio por mercado y el total, ordenado de mayor a menor.
    Los pesos se normalizan para que sumen 1, asi que puedes escribirlos en % o en fracciones.
    """
    pesos = pd.Series(pesos, dtype=float)
    pesos = pesos / pesos.sum()
    contribucion = puntajes.mul(pesos, axis=0)
    resultado = contribucion.T
    resultado["Total"] = resultado.sum(axis=1)
    return resultado.sort_values("Total", ascending=False)
''',
}


def cell_metricas(claves):
    cuerpo = "\n\n".join(METRICAS[k].strip("\n") for k in claves)
    return code("# ============================================================\n"
                "#  Formulas: las mismas de los cuadernos 2, 3 y 4 del curso\n"
                "# ============================================================\n\n" + cuerpo + "\n\nprint('Formulas listas.')")


def cierre(referencias):
    refs = "\n\n".join(referencias)
    return md(f"""
---
# Entrega

1. Revisa que todas las celdas **Análisis del equipo** tengan texto.
2. `Archivo → Descargar → Descargar .ipynb`.
3. Sube el archivo al aula virtual. Las figuras y tablas de `salidas/` pueden ir al informe escrito.

# Referencias

{refs}

International Trade Centre. (2025). *Trade Map: Trade statistics for international business development*. https://www.trademap.org

Durán Lima, J. E. (s.f.). *Indicadores de comercio exterior y política comercial: Generalidades metodológicas e indicadores básicos*. CEPAL.

McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*, 56–61. https://doi.org/10.25080/Majora-92bf1922-00a

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering, 9*(3), 90–95. https://doi.org/10.1109/MCSE.2007.55
""")


REF_BALASSA = "Balassa, B. (1965). Trade liberalisation and \"revealed\" comparative advantage. *The Manchester School, 33*(2), 99–123."
REF_VOLLRATH = "Vollrath, T. L. (1991). A theoretical evaluation of alternative trade intensity measures of revealed comparative advantage. *Weltwirtschaftliches Archiv, 127*(2), 265–280."
REF_YU = "Yu, R., Cai, J., & Leung, P. (2009). The normalized revealed comparative advantage index. *The Annals of Regional Science, 43*(1), 267–282."
REF_GL = "Grubel, H. G., & Lloyd, P. J. (1975). *Intra-industry trade*. Macmillan."
REF_WB = "World Bank. (2025). *World Development Indicators*. https://data.worldbank.org"
REF_FAO = "FAO. (2025). *FAOSTAT: Crops and livestock products*. https://www.fao.org/faostat"
REF_BAENA = "Baena-Rojas, J. J., & Cano, J. A. (2026). International market selection for exports of goods: A data analysis technique for organizational decision-making. *Global Business Review*. https://doi.org/10.1177/09721509261464305"
REF_LAFAY = "Lafay, G. (1992). The measurement of revealed comparative advantages. En M. G. Dagenais & P. A. Muet (Eds.), *International Trade Modelling* (pp. 209–234). Chapman & Hall."


def escribir(celdas, ruta_relativa):
    nb = nbf.v4.new_notebook()
    nb["cells"] = celdas
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    }
    destino = os.path.join(RAIZ, ruta_relativa)
    nbf.write(nb, destino)
    print("escrito:", destino)
    return destino
