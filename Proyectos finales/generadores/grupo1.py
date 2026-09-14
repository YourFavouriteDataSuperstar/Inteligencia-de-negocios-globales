from comun import *

G = "Proyectos finales/Grupo 1"
D = G + "/datos/"
G6 = "Proyectos finales/Grupo 6/datos/Anexo_Datos_Curuba_Equipo6/03_datos_limpios/"
NB = G + "/Grupo_1_Uchuva.ipynb"

ARCHIVOS = {
    "exp_2025_xlsx": D + "colombias-exports-to-world-in-2025-by-importer_081090.xlsx",
    "imp_2025_xlsx": D + "colombias-imports-from-world-in-2025-by-exporter_081090.xlsx",
    "exp_serie":     D + "colombias-exports-to-world-by-importer_081090.csv",
    "pib":           D + "API_NY.GDP.MKTP.CD_DS2_es_csv_v2_35933/API_NY.GDP.MKTP.CD_DS2_es_csv_v2_35933.csv",
    "mundo_serie":   G6 + "t2_exportadores_081090_largo.csv",
    "mundo_total":   G6 + "t3_mundo_081090.csv",
    "canasta_co_exp":    "data/co_exp_productos_hs2_serie.xls",
    "canasta_mundo_exp": "data/mundo_exp_productos_hs2_serie.csv",
}

METR = [
    ("Participación de mercado por destino", "¿A quién le vende Colombia la subpartida de la uchuva y con qué peso?"),
    ("CR3 y HHI", "¿Qué tan concentradas están las exportaciones en pocos destinos, y cómo ha cambiado?"),
    ("Valor FOB por kilo", "¿En qué destinos se paga mejor el producto?"),
    ("Crecimiento y CAGR", "¿Qué destinos crecen y a qué ritmo?"),
    ("VCR de Balassa", "¿Colombia exporta proporcionalmente más de este producto que el resto del mundo?"),
    ("PIB de los mercados candidatos", "¿Qué tamaño tienen las economías a las que se quiere llegar?"),
    ("Matriz de mercados", "¿Cuáles tres mercados se seleccionan entre al menos cinco candidatos?"),
]

celdas = [
    badge(NB),
    portada("Grupo 1. Oportunidad de exportación de la uchuva colombiana",
            "Grupo 1", "Uchuva fresca (*Physalis peruviana*), subpartida nacional 0810905000. En las bases internacionales solo existe **HS 081090** (\"otros frutos frescos\"), que agrupa uchuva, maracuyá, pitahaya y otros; todos los indicadores se leen a ese nivel.",
            "¿Cómo puede Colombia fortalecer la competitividad de la uchuva y disminuir la dependencia de sus principales mercados de exportación?",
            METR, "*Equipo 1 — Ficha técnica* (septiembre de 2026). De los archivos entregados se usan los de HS 081090; los dos de HS 081020 (frambuesas y moras) corresponden a otro producto y no se usan. La serie 2016-2025 por destino se descargó de Trade Map para este cuaderno."),
    md("---\n# 0. Preparación del entorno"),
    CELL_IMPORTS,
    cell_config(G, ARCHIVOS),
    CELL_DESCARGA,
    CELL_LECTORES,
    cell_metricas(["hhi", "cr", "rca", "cagr", "multicriterio"]),

    md("---\n# 1. Los datos y una trampa nueva\n\nEl archivo de exportaciones 2025 llegó como `.xlsx`, pero cada fila tiene el texto completo de una línea CSV metido en una sola celda, y con la codificación dañada (`maracuyÃ¡`). El lector de abajo reconstruye el texto, repara la codificación y lo interpreta como CSV. El archivo de importaciones sí está bien tabulado."),
    code('''
def leer_trademap_xlsx_roto(ruta_archivo):
    """Reconstruye una tabla de Trade Map cuyo xlsx trae una linea CSV completa por celda."""
    import openpyxl
    libro = openpyxl.load_workbook(ruta_archivo, read_only=True)
    hoja = libro.active
    lineas = [str(fila[0]) for fila in hoja.iter_rows(values_only=True) if fila and fila[0] is not None]
    texto = "\\n".join(lineas)
    try:
        texto = texto.encode("latin-1").decode("utf-8")      # repara "maracuyÃ¡" -> "maracuyá"
    except UnicodeError:
        pass
    tabla = pd.read_csv(io.StringIO(texto), dtype={"reporterCd": str, "partnerCd": str, "productCd": str})
    return limpiar_trademap(tabla)


def leer_trademap_xlsx(ruta_archivo):
    """Lee una tabla de Trade Map guardada como Excel normal."""
    tabla = pd.read_excel(ruta_archivo, dtype={"reporterCd": str, "partnerCd": str, "productCd": str})
    return limpiar_trademap(tabla)


exp_2025 = leer_trademap_xlsx_roto(ruta("exp_2025_xlsx"))
imp_2025 = leer_trademap_xlsx(ruta("imp_2025_xlsx"))
serie    = leer_serie_trademap(ruta("exp_serie"))
mundo_serie = pd.read_csv(ruta("mundo_serie"), dtype={"codigo_tm": str})      # exportadores mundiales 2016-2025 (grupo 6)
mundo_total = pd.read_csv(ruta("mundo_total"))                                  # el mundo, 2016-2025
canasta_co_exp    = leer_canasta(ruta("canasta_co_exp"))
canasta_mundo_exp = leer_canasta(ruta("canasta_mundo_exp"))

mundo_2025, destinos_2025 = separar_mundo(exp_2025)
mundo_imp_2025, origenes_2025 = separar_mundo(imp_2025)
print(f"Colombia exporto HS 081090 por USD {mundo_2025['valor_kusd']:,.0f} miles en 2025 ({mundo_2025['cantidad']:,.0f} t) a {len(destinos_2025)} destinos")
print(f"Colombia importo HS 081090 por USD {mundo_imp_2025['valor_kusd']:,.0f} miles, sobre todo de {origenes_2025.iloc[0]['pais']}")
destinos_2025[["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_pct", "cuota_en_socio_pct", "crec_valor_5a_pct", "crec_importaciones_socio_5a_pct"]].head(10)
'''),
    code('''
pib = leer_banco_mundial(ruta("pib"), "pib_usd")
pib.dropna().groupby("anio").size().tail(3)   # cuantos paises tienen dato en los ultimos anios
'''),

    md("---\n# 2. Participación de mercado por destino"),
    code('''
participacion = destinos_2025.nlargest(12, "valor_kusd")[["pais", "valor_kusd", "cantidad", "participacion_pct"]]
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = participacion.sort_values("participacion_pct")
ax.barh(orden["pais"], orden["participacion_pct"], color=AZUL, height=0.6)
for y, v in enumerate(orden["participacion_pct"]):
    ax.annotate(f"{v:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Participación de cada destino en las exportaciones colombianas de HS 081090, 2025", "Doce mayores destinos",
       "Trade Map (ITC), 2025.", eje_x="% del valor exportado", rejilla="x")
guardar(fig, "g1_participacion_2025")
exportar(participacion, "g1_participacion_2025")
'''),
    code('''
paises_serie = serie[serie["codigo"] != "000"]
top4 = paises_serie[paises_serie["anio"] == 2025].nlargest(4, "valor_kusd")["pais"].tolist()
series_top = (paises_serie.assign(grupo=lambda d: np.where(d["pais"].isin(top4), d["pais"], "Otros"))
                          .groupby(["anio", "grupo"])["valor_kusd"].sum().unstack("grupo")[top4 + ["Otros"]])
participacion_serie = series_top.div(series_top.sum(axis=1), axis=0) * 100
exportar(participacion_serie.reset_index(), "g1_participacion_serie")

fig, ax = plt.subplots(figsize=(10, 5))
colores = CATEGORIAS + [GRIS_MID]
ax.stackplot(participacion_serie.index, [participacion_serie[c] for c in participacion_serie.columns], colors=colores, labels=participacion_serie.columns, alpha=0.9)
ax.set_ylim(0, 100)
ax.set_xticks(participacion_serie.index)
leyenda_fuera(ax)
estilo(ax, "Participación de cada destino, 2016-2025", "% del valor exportado cada año; cuatro mayores destinos de 2025 y el resto", "Trade Map (ITC), 2025.", eje_y="%")
guardar(fig, "g1_participacion_serie")
participacion_serie.round(1)
'''),
    analisis("¿Qué tan dependiente es el producto de un solo comprador y desde cuándo?"),

    md("---\n# 3. Concentración: CR3 y HHI, 2016-2025"),
    code('''
concentracion = (paises_serie.groupby("anio")["valor_kusd"]
                 .agg(HHI=hhi, CR3=lambda v: cr_n(v, 3), destinos_activos=lambda v: int((v > 0).sum()))
                 .reset_index())
concentracion["numero_equivalente"] = numeros_equivalentes(concentracion["HHI"])
exportar(concentracion, "g1_concentracion")
concentracion
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
axes[0].plot(concentracion["anio"], concentracion["HHI"], color=AZUL, linewidth=2.4, marker="o", markersize=7)
for _, fila in concentracion.iterrows():
    axes[0].annotate(f"{fila['HHI']:.3f}", (fila["anio"], fila["HHI"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].axhspan(0.18, 1, color=ROJO, alpha=0.06)
axes[0].axhspan(0.15, 0.18, color=NARANJA, alpha=0.06)
axes[0].set_ylim(0, max(0.6, concentracion["HHI"].max() * 1.2))
axes[0].set_xticks(concentracion["anio"])
estilo(axes[0], "HHI de destinos", "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", eje_y="HHI")
axes[1].plot(concentracion["anio"], concentracion["CR3"], color=VERDE, linewidth=2.4, marker="o", markersize=7)
for _, fila in concentracion.iterrows():
    axes[1].annotate(f"{fila['CR3']:.0f} %", (fila["anio"], fila["CR3"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].set_ylim(0, 105)
axes[1].set_xticks(concentracion["anio"])
estilo(axes[1], "CR3: peso de los tres mayores destinos", "% del valor exportado", "Trade Map (ITC), 2025.", eje_y="%")
plt.tight_layout()
guardar(fig, "g1_concentracion")
'''),
    analisis(),

    md("---\n# 4. Valor FOB por kilo\n\nTrade Map entrega `valor_unitario` en USD por tonelada: se divide por 1.000 para tenerlo en USD por kilo."),
    code('''
fob_kg = destinos_2025.nlargest(12, "valor_kusd").copy()
fob_kg = fob_kg[fob_kg["cantidad"] > 0]
fob_kg["fob_usd_kg"] = fob_kg["valor_unitario"] / 1000
promedio_kg = mundo_2025["valor_unitario"] / 1000
fob_kg = fob_kg[["pais", "valor_kusd", "cantidad", "fob_usd_kg"]]
exportar(fob_kg, "g1_fob_por_kilo")
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = fob_kg.sort_values("fob_usd_kg")
ax.barh(orden["pais"], orden["fob_usd_kg"], color=AZUL, height=0.6)
ax.axvline(promedio_kg, color=NARANJA, linewidth=1.5, linestyle="--")
ax.annotate(f"promedio Colombia {promedio_kg:.2f}", (promedio_kg, len(orden) - 0.4), xytext=(4, 0), textcoords="offset points", fontsize=9, color=NARANJA)
for y, v in enumerate(orden["fob_usd_kg"]):
    ax.annotate(f"{v:.2f}", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Valor FOB por kilo según destino, 2025", "USD/kg = valor exportado / kilos netos; doce mayores destinos",
       "Trade Map (ITC), 2025.", eje_x="USD por kilo", rejilla="x")
guardar(fig, "g1_fob_por_kilo")
fob_kg
'''),
    analisis(),

    md("---\n# 5. Crecimiento y CAGR por destino"),
    code('''
ancho = paises_serie.pivot(index="pais", columns="anio", values="valor_kusd")
top10 = ancho[2025].nlargest(10).index
tabla_cagr = pd.DataFrame({
    "valor_2016": ancho.loc[top10, 2016],
    "valor_2020": ancho.loc[top10, 2020],
    "valor_2025": ancho.loc[top10, 2025],
    "cagr_2016_2025_pct": [cagr(ancho.loc[p, 2016], ancho.loc[p, 2025], 9) for p in top10],
    "cagr_2020_2025_pct": [cagr(ancho.loc[p, 2020], ancho.loc[p, 2025], 5) for p in top10],
}).reset_index()
total = serie[serie["codigo"] == "000"].set_index("anio")["valor_kusd"]
print(f"CAGR total HS 081090 2016-2025: {cagr(total[2016], total[2025], 9):.1f} %   |   2020-2025: {cagr(total[2020], total[2025], 5):.1f} %")
exportar(tabla_cagr, "g1_cagr")
tabla_cagr
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(total.index.astype(str), total.values, color=AZUL, width=0.6)
for x, v in enumerate(total.values):
    axes[0].annotate(fmt_miles(v), (x, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5, color=GRIS_TEXT)
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
estilo(axes[0], "Exportaciones colombianas de HS 081090", "USD, 2016-2025", eje_y="USD")
orden = tabla_cagr.sort_values("cagr_2016_2025_pct")
colores = [ROJO if v < 0 else AZUL for v in orden["cagr_2016_2025_pct"]]
axes[1].barh(orden["pais"], orden["cagr_2016_2025_pct"], color=colores, height=0.6)
for y, v in enumerate(orden["cagr_2016_2025_pct"]):
    axes[1].annotate(f"{v:+.1f} %", (v, y), textcoords="offset points", xytext=(4 if v >= 0 else -4, 0), ha="left" if v >= 0 else "right", va="center", fontsize=9, color=GRIS_TEXT)
axes[1].axvline(0, color=GRIS_EJE, linewidth=0.8)
estilo(axes[1], "CAGR por destino, 2016-2025", "Diez mayores destinos de 2025", "Trade Map (ITC), 2025.", eje_x="CAGR (%)", rejilla="x")
plt.tight_layout()
guardar(fig, "g1_crecimiento")
'''),
    analisis(),

    md("---\n# 6. Ventaja comparativa revelada de Balassa\n\nNumerador: exportaciones colombianas de HS 081090 (Trade Map) y exportaciones mundiales del mismo código (serie del grupo 6, también de Trade Map). Denominador: exportaciones totales de Colombia y del mundo, fila TOTAL de la canasta HS2 del curso. Se calcula también para el capítulo 08 completo (frutas) con la serie 2021-2025.\n\nOjo: la cobertura mundial de 2025 en Trade Map es parcial (no todos los países han reportado), por eso se muestran 2024 y 2025."),
    code('''
vcr = []
for anio in (2024, 2025):
    X_ij = total[anio]
    X_i  = fila_canasta(canasta_co_exp, "TOTAL")[str(anio)]
    X_j  = mundo_total.set_index("anio").loc[anio, "exportaciones_mundiales_usd_miles"]
    X_w  = fila_canasta(canasta_mundo_exp, "TOTAL")[str(anio)]
    r = float(rca_balassa(X_ij, X_i, X_j, X_w))
    vcr.append({"anio": anio, "X_ij": X_ij, "X_i": X_i, "X_j": X_j, "X_w": X_w, "RCA_081090": r, "RSCA_081090": float(rsca_laursen(r))})
vcr = pd.DataFrame(vcr)

vcr_cap08 = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA]})
vcr_cap08["RCA_cap08"] = rca_balassa(fila_canasta(canasta_co_exp, "08"), fila_canasta(canasta_co_exp, "TOTAL"),
                                     fila_canasta(canasta_mundo_exp, "08"), fila_canasta(canasta_mundo_exp, "TOTAL"))
vcr_cap08["RSCA_cap08"] = rsca_laursen(vcr_cap08["RCA_cap08"])
exportar(vcr, "g1_rca_081090"); exportar(vcr_cap08, "g1_rca_cap08")
display(vcr); vcr_cap08
'''),
    code('''
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.plot(vcr_cap08["anio"], vcr_cap08["RCA_cap08"], color=VERDE, linewidth=2.2, marker="o", markersize=6, label="Capítulo 08 (frutas y frutos secos)")
ax.plot(vcr["anio"], vcr["RCA_081090"], color=AZUL, linewidth=2.2, marker="o", markersize=7, label="HS 081090 (otros frutos frescos)")
for _, f in vcr_cap08.iterrows():
    ax.annotate(f"{f['RCA_cap08']:.1f}", (f["anio"], f["RCA_cap08"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
for _, f in vcr.iterrows():
    ax.annotate(f"{f['RCA_081090']:.1f}", (f["anio"], f["RCA_081090"]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color=GRIS_TEXT)
ax.axhline(1, color=GRIS_EJE, linewidth=0.8, linestyle="--")
ax.set_xticks(vcr_cap08["anio"])
ax.set_ylim(0, max(vcr_cap08["RCA_cap08"].max(), vcr["RCA_081090"].max()) * 1.25)
ax.legend(frameon=False, fontsize=9, loc="upper left")
estilo(ax, "RCA de Balassa: Colombia", "Línea punteada = 1 (umbral de ventaja comparativa revelada)", "Trade Map (ITC), 2025; canasta HS2 del curso.", eje_y="RCA")
guardar(fig, "g1_rca")
'''),
    analisis("¿La ventaja es del producto o de toda la fruticultura colombiana? ¿Qué implica que HS 081090 mezcle varias frutas?"),

    md("---\n# 7. PIB de los mercados candidatos\n\nLos candidatos se toman de los mayores destinos de 2025. La lista es **editable**: cambia los pares `nombre en Trade Map: código ISO3` para evaluar otros mercados."),
    code('''
# ====================== EDITABLE: mercados candidatos (nombre Trade Map -> ISO3) ======================
CANDIDATOS = {
    "Países Bajos": "NLD", "Reino Unido": "GBR", "Alemania": "DEU", "Estados Unidos de América": "USA",
    "Canadá": "CAN", "España": "ESP", "Bélgica": "BEL", "Emiratos Árabes Unidos": "ARE",
}
# ======================================================================================================
pib_reciente = (pib.dropna(subset=["pib_usd"]).sort_values("anio").groupby("iso3").tail(1)
                   .set_index("iso3")[["pais", "anio", "pib_usd"]].rename(columns={"pais": "pais_bm", "anio": "anio_pib"}))
tablero = destinos_2025.set_index("pais").reindex(CANDIDATOS.keys())[
    ["valor_kusd", "participacion_pct", "cuota_en_socio_pct", "ranking_socio", "crec_valor_5a_pct", "crec_importaciones_socio_5a_pct", "valor_unitario"]]
tablero["iso3"] = pd.Series(CANDIDATOS)
tablero = tablero.join(pib_reciente, on="iso3")
tablero["pib_usd_mil_mn"] = tablero["pib_usd"] / 1e9
exportar(tablero.reset_index(), "g1_tablero_candidatos")
tablero
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
orden = tablero.sort_values("pib_usd_mil_mn")
axes[0].barh(orden.index, orden["pib_usd_mil_mn"], color=AZUL, height=0.6)
for y, (v, a) in enumerate(zip(orden["pib_usd_mil_mn"], orden["anio_pib"])):
    axes[0].annotate(f"{v:,.0f}  ({a:.0f})", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
axes[0].set_xscale("log")
estilo(axes[0], "PIB de los candidatos", "Miles de millones de USD, último año con dato (escala log)", eje_x="USD (miles de millones)", rejilla="x")
puntos = tablero.dropna(subset=["cuota_en_socio_pct", "crec_importaciones_socio_5a_pct"])
tamanos = puntos["valor_kusd"] / puntos["valor_kusd"].max() * 900 + 40
axes[1].scatter(puntos["cuota_en_socio_pct"], puntos["crec_importaciones_socio_5a_pct"], s=tamanos, color=AZUL, alpha=0.55, edgecolor="white", linewidth=1.5)
for nombre, p in puntos.iterrows():
    axes[1].annotate(nombre, (p["cuota_en_socio_pct"], p["crec_importaciones_socio_5a_pct"]), textcoords="offset points", xytext=(6, 4), fontsize=8.5, color=GRIS_TEXT)
estilo(axes[1], "Cuota de Colombia y crecimiento de la demanda", "Tamaño del punto = valor exportado por Colombia, 2025", "Banco Mundial (WDI) y Trade Map (ITC), 2025.",
       eje_x="Cuota de Colombia en las importaciones del destino (%)", eje_y="Crecimiento de las importaciones del destino, 5 años (%)")
plt.tight_layout()
guardar(fig, "g1_candidatos")
'''),
    analisis(),

    md("---\n# 8. Matriz de mercados\n\nLa ficha pide evaluar **al menos cinco mercados** y seleccionar **hasta tres**. Cuatro criterios salen de los datos (valor actual exportado, crecimiento de las importaciones del destino, cuota de Colombia y PIB); dos son **editables** porque requieren ICA, Legiscomex o Analdex: facilidad de acceso fitosanitario y arancel. Los pesos también son editables. Cada criterio se lleva a 0-100 según su dirección."),
    code('''
# ====================== EDITABLE: pesos y criterios manuales ======================
PESOS = {
    "Valor exportado por Colombia 2025": 20,
    "Crecimiento de las importaciones del destino, 5 años": 20,
    "Cuota actual de Colombia": 15,
    "PIB": 15,
    "Facilidad de acceso fitosanitario (1-5)": 15,     # manual: mayor es mejor
    "Arancel a Colombia (%)": 15,                      # manual: menor es mejor
}
MANUAL = pd.DataFrame({
    "Facilidad de acceso fitosanitario (1-5)": [3] * len(CANDIDATOS),
    "Arancel a Colombia (%)": [0] * len(CANDIDATOS),
}, index=list(CANDIDATOS.keys())).T
# ==================================================================================
VARIABLES = pd.DataFrame({
    "Valor exportado por Colombia 2025": tablero["valor_kusd"],
    "Crecimiento de las importaciones del destino, 5 años": tablero["crec_importaciones_socio_5a_pct"],
    "Cuota actual de Colombia": tablero["cuota_en_socio_pct"],
    "PIB": tablero["pib_usd"],
}).T
VARIABLES = pd.concat([VARIABLES, MANUAL]).astype(float)
DIRECCION = {v: +1 for v in VARIABLES.index}
DIRECCION["Arancel a Colombia (%)"] = -1

def a_escala_100(fila, direccion):
    """Min-max a 0-100 en la direccion indicada. Si todos son iguales, 50."""
    if fila.max() == fila.min():
        return pd.Series(50.0, index=fila.index)
    escala = (fila - fila.min()) / (fila.max() - fila.min()) * 100
    return escala if direccion > 0 else 100 - escala

PUNTAJES = pd.DataFrame({v: a_escala_100(VARIABLES.loc[v], DIRECCION[v]) for v in VARIABLES.index}).T
matriz = matriz_multicriterio(PUNTAJES, PESOS)
print("Variables crudas:"); display(VARIABLES.round(2))
exportar(matriz.reset_index().rename(columns={"index": "mercado"}), "g1_matriz_mercados")
matriz.round(1)
'''),
    code('''
fig, ax = plt.subplots(figsize=(10, 5))
acumulado = np.zeros(len(matriz))
paleta = CATEGORIAS + ["#7f7d76", GRIS_MID]
for color, criterio in zip(paleta, PESOS.keys()):
    ax.barh(matriz.index, matriz[criterio], left=acumulado, color=color, height=0.6, label=criterio, edgecolor="white", linewidth=1.5)
    acumulado += matriz[criterio].values
for y, t in enumerate(matriz["Total"]):
    ax.annotate(f"{t:.0f}", (t, y), textcoords="offset points", xytext=(5, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.invert_yaxis()
ax.set_xlim(0, 110)
leyenda_fuera(ax)
estilo(ax, "Matriz de mercados: puntaje ponderado (0-100)", "Los tres primeros serían los mercados seleccionados", "Trade Map, Banco Mundial y elaboración del equipo.", eje_x="Puntaje", rejilla="x")
guardar(fig, "g1_matriz_mercados")
'''),
    analisis("¿Cuáles tres mercados quedan seleccionados y qué cambia si llenan los criterios manuales con datos del ICA y Legiscomex?"),

    md("---\n# 9. Cadena de valor, actores y requisitos (OE4)\n\nEste objetivo es cualitativo (EMIS, ICA, Analdex, Legiscomex) y no lleva código.\n\n**Mapa de actores y requisitos del equipo:**\n\n_(escriban aquí)_"),

    cierre([REF_BALASSA, REF_WB, REF_BAENA]),
]

escribir(celdas, NB)
