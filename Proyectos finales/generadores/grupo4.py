from comun import *

G = "Proyectos finales/Grupo 4"
D = G + "/datos/"
NB = G + "/Grupo_4_Esmeraldas.ipynb"

ARCHIVOS = {
    "exp_2025":   D + "EXPORTACIONES DE COLOMBIA AL MUNDO.csv",
    "brasil_2025": D + "EXPORTACIONES DE BRAZIL HACIA EL MUNDO.csv",
    "mundo_exp":  D + "EXPORTACIONES DEL MUNDO.csv",
    "cap71_exp":  D + "EXPORTACIONES COLOMBIA HACIA EL MUNDO CAPITULO 71.csv",
    "cap71_imp":  D + "IMPORTACIONES COLOMBIA HACIA EL MUNDO CAPITULO 71.csv",
    "exp_serie":  D + "colombias-exports-to-world-by-importer_710391.csv",
    "wb_pib": "data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_234.csv",
    "wb_exp": "data/API_NE.EXP.GNFS.CD_DS2_en_csv_v2_35140.csv",
    "wb_imp": "data/API_NE.IMP.GNFS.CD_DS2_en_csv_v2_33330.csv",
    "canasta_co_exp":    "data/co_exp_productos_hs2_serie.xls",
    "canasta_co_imp":    "data/co_imp_productos_hs2_serie.csv",
    "canasta_mundo_exp": "data/mundo_exp_productos_hs2_serie.csv",
}

METR = [
    ("Participación por destino", "¿A quién le vende Colombia sus esmeraldas talladas?"),
    ("HHI, Theil y número equivalente", "¿Qué tan concentrados están los destinos y cómo ha cambiado desde 2016?"),
    ("Crecimiento exportador", "¿Crecen o caen las exportaciones año a año?"),
    ("RCA, RSCA y NRCA", "¿Colombia, Brasil y Etiopía están especializados en HS 710391?"),
    ("Apertura comercial e IBCR de los mercados", "¿Qué tan abiertas son la UE, Emiratos, Singapur y Suiza?"),
    ("Grubel-Lloyd del capítulo 71", "¿El comercio de piedras y metales preciosos es interindustrial o intraindustrial?"),
    ("Crecimiento de importaciones y participación de Colombia", "¿En qué destinos crece la demanda y cuánto de ella es colombiana?"),
    ("Ficha financiera EMIS", "¿Cómo les va a las comercializadoras esmeralderas?"),
]

celdas = [
    badge(NB),
    portada("Grupo 4. Sector esmeraldero colombiano: métricas de comercio exterior para una hoja de ruta",
            "Grupo 4", "Esmeraldas talladas, **HS 710391** (rubíes, zafiros y esmeraldas: el código no aísla la esmeralda, como advierte la ficha). Estructura comercial con el **capítulo 71**.",
            "¿Cómo reducir la vulnerabilidad por concentración de destinos, enfrentar la presión competitiva de otros productores y acceder a segmentos de mayor valor agregado?",
            METR, "*Ficha técnica del estudio — Sector esmeraldero* (2026). La serie 2016-2025 por destino se descargó de Trade Map para este cuaderno. Los tres reportes EMIS no se redistribuyen: el cuaderno los pide al ejecutarse."),
    md("---\n# 0. Preparación del entorno"),
    CELL_IMPORTS,
    cell_config(G, ARCHIVOS),
    CELL_DESCARGA,
    CELL_LECTORES,
    cell_metricas(["hhi", "cr", "theil", "gl", "ibcr", "apertura", "rca", "nrca", "cagr"]),

    md("---\n# 1. Los datos\n\nCinco CSV de Trade Map del equipo (cortes de 2025), la serie 2016-2025 por destino, tres archivos del Banco Mundial (PIB, exportaciones e importaciones totales) y la canasta HS2 del curso.\n\nDos trampas de los archivos del equipo: en `EXPORTACIONES DE COLOMBIA AL MUNDO.csv` la cantidad viene en cero para todos los destinos (el valor unitario no es calculable), y en el archivo de importaciones del capítulo 71 la columna `Balance` repite el balance de las exportaciones, así que solo se usa `Value`."),
    code('''
exp_2025   = leer_trademap(ruta("exp_2025"))       # Colombia exporta 710391 por destino, 2025
brasil     = leer_trademap(ruta("brasil_2025"))    # Brasil exporta 710391 por destino, 2025
mundo_exp  = leer_trademap(ruta("mundo_exp"))      # exportadores mundiales de 710391, 2025
cap71_exp  = leer_trademap(ruta("cap71_exp"))      # Colombia exporta capitulo 71 por destino, 2025
cap71_imp  = leer_trademap(ruta("cap71_imp"))      # Colombia importa capitulo 71 por origen, 2025
serie      = leer_serie_trademap(ruta("exp_serie"))
wb_pib = leer_banco_mundial(ruta("wb_pib"), "pib_usd")
wb_exp = leer_banco_mundial(ruta("wb_exp"), "exportaciones_usd")
wb_imp = leer_banco_mundial(ruta("wb_imp"), "importaciones_usd")
canasta_co_exp, canasta_co_imp, canasta_mundo_exp = (leer_canasta(ruta(k)) for k in ("canasta_co_exp", "canasta_co_imp", "canasta_mundo_exp"))

mundo_2025, destinos_2025 = separar_mundo(exp_2025)
mundo_oferta, exportadores = separar_mundo(mundo_exp)
print(f"Colombia exporto HS 710391 por USD {mundo_2025['valor_kusd']:,.0f} miles en 2025 a {len(destinos_2025)} destinos (se excluye la fila 'Zona franca')")
print(f"El mundo exporto HS 710391 por USD {mundo_oferta['valor_kusd']:,.0f} miles; Colombia es el exportador n.º {int(exportadores.reset_index().index[exportadores['pais'] == 'Colombia'][0]) + 1}")
destinos_2025[["pais", "valor_kusd", "participacion_pct", "cuota_en_socio_pct", "ranking_socio", "crec_valor_5a_pct", "crec_importaciones_socio_5a_pct"]].head(10)
'''),

    md("---\n# 2. Participación por destino"),
    code('''
participacion = destinos_2025.nlargest(12, "valor_kusd")[["pais", "valor_kusd", "participacion_pct"]]
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = participacion.sort_values("participacion_pct")
ax.barh(orden["pais"], orden["participacion_pct"], color=AZUL, height=0.6)
for y, v in enumerate(orden["participacion_pct"]):
    ax.annotate(f"{v:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Participación de cada destino en las exportaciones colombianas de HS 710391, 2025", "Doce mayores destinos",
       "Trade Map (ITC), 2025.", eje_x="% del valor exportado", rejilla="x")
guardar(fig, "g4_participacion_2025")
exportar(participacion, "g4_participacion_2025")
'''),
    code('''
paises_serie = serie[serie["codigo"] != "000"]
paises_serie = paises_serie[~paises_serie["pais"].isin(AGREGADOS_NO_PAIS)]
top4 = paises_serie[paises_serie["anio"] == 2025].nlargest(4, "valor_kusd")["pais"].tolist()
series_top = (paises_serie.assign(grupo=lambda d: np.where(d["pais"].isin(top4), d["pais"], "Otros"))
                          .groupby(["anio", "grupo"])["valor_kusd"].sum().unstack("grupo")[top4 + ["Otros"]])
exportar(series_top.reset_index(), "g4_series_destinos")
fig, ax = plt.subplots(figsize=(10, 5))
for color, columna in zip(CATEGORIAS + [GRIS_MID], series_top.columns):
    ax.plot(series_top.index, series_top[columna], color=color, linewidth=2.2, marker="o", markersize=5, label=columna)
ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
ax.set_xticks(series_top.index)
ax.legend(frameon=False, fontsize=9, loc="upper right")
estilo(ax, "Exportaciones colombianas de HS 710391 por destino, 2016-2025", "USD; cuatro mayores destinos de 2025 y el resto", "Trade Map (ITC), 2025.", eje_y="USD")
guardar(fig, "g4_series_destinos")
'''),
    analisis(),

    md("---\n# 3. Concentración: HHI, Theil y número equivalente, 2016-2025"),
    code('''
concentracion = (paises_serie.groupby("anio")["valor_kusd"]
                 .agg(HHI=hhi, Theil=theil, CR3=lambda v: cr_n(v, 3), destinos_activos=lambda v: int((v > 0).sum()))
                 .reset_index())
concentracion["numero_equivalente"] = numeros_equivalentes(concentracion["HHI"])
exportar(concentracion, "g4_concentracion")
concentracion
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
axes[0].plot(concentracion["anio"], concentracion["HHI"], color=AZUL, linewidth=2.4, marker="o", markersize=7)
for _, f in concentracion.iterrows():
    axes[0].annotate(f"{f['HHI']:.3f}", (f["anio"], f["HHI"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].axhspan(0.18, 1, color=ROJO, alpha=0.06)
axes[0].axhspan(0.15, 0.18, color=NARANJA, alpha=0.06)
axes[0].set_ylim(0, max(0.6, concentracion["HHI"].max() * 1.2))
axes[0].set_xticks(concentracion["anio"])
estilo(axes[0], "HHI de destinos", "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", eje_y="HHI")
axes[1].plot(concentracion["anio"], concentracion["Theil"], color=VERDE, linewidth=2.4, marker="o", markersize=7)
for _, f in concentracion.iterrows():
    axes[1].annotate(f"{f['Theil']:.2f}", (f["anio"], f["Theil"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].set_ylim(0, concentracion["Theil"].max() * 1.25)
axes[1].set_xticks(concentracion["anio"])
estilo(axes[1], "Índice de Theil de destinos", "0 = reparto igual entre destinos activos; sube con la desigualdad", "Trade Map (ITC), 2025.", eje_y="Theil")
plt.tight_layout()
guardar(fig, "g4_concentracion")
'''),
    analisis("HHI y Theil no siempre cuentan la misma historia. ¿Coinciden aquí?"),

    md("---\n# 4. Crecimiento exportador"),
    code('''
total = serie[serie["codigo"] == "000"].set_index("anio")["valor_kusd"]
crecimiento = pd.DataFrame({"valor_kusd": total})
crecimiento["variacion_interanual_pct"] = crecimiento["valor_kusd"].pct_change() * 100
print(f"CAGR 2016-2025: {cagr(total[2016], total[2025], 9):+.1f} %   |   2020-2025: {cagr(total[2020], total[2025], 5):+.1f} %")
print(f"Trade Map reporta para 2025: crecimiento 5 años {mundo_2025['crec_valor_5a_pct']:+.0f} %, 2 años {mundo_2025['crec_valor_2a_pct']:+.0f} %")
exportar(crecimiento.reset_index(), "g4_crecimiento")
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
axes[0].bar(total.index.astype(str), total.values, color=AZUL, width=0.6)
for x, v in enumerate(total.values):
    axes[0].annotate(fmt_miles(v), (x, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5, color=GRIS_TEXT)
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
estilo(axes[0], "Exportaciones colombianas de HS 710391", "USD, 2016-2025", eje_y="USD")
var = crecimiento["variacion_interanual_pct"].dropna()
axes[1].bar(var.index.astype(str), var.values, color=[ROJO if v < 0 else AZUL for v in var.values], width=0.6)
for x, v in enumerate(var.values):
    axes[1].annotate(f"{v:+.0f} %", (x, v), textcoords="offset points", xytext=(0, 4 if v >= 0 else -12), ha="center", fontsize=8.5, color=GRIS_TEXT)
axes[1].axhline(0, color=GRIS_EJE, linewidth=0.8)
estilo(axes[1], "Variación interanual", "(X_t - X_t-1) / X_t-1 x 100", "Trade Map (ITC), 2025.", eje_y="%")
plt.tight_layout()
guardar(fig, "g4_crecimiento")
crecimiento
'''),
    analisis(),

    md("---\n# 5. Ventaja comparativa revelada: RCA, RSCA y NRCA\n\nPara comparar países se necesitan sus **exportaciones totales**, que no están en las descargas del equipo. Se usan las exportaciones de bienes y servicios del Banco Mundial (una aproximación: incluyen servicios) para el último año con dato de todos los países. Zambia, nombrado en la ficha, **no aparece en la descarga mundial de HS 710391**, así que no se puede calcular.\n\nPara Colombia se calcula además la serie 2021-2025 del capítulo 71 completo con la canasta del curso."),
    code('''
COMPARADORES = {"Colombia": "COL", "Brasil": "BRA", "Etiopía": "ETH", "Zambia": "ZMB"}
ANIO_WB = 2024
totales_wb = wb_exp[wb_exp["anio"] == ANIO_WB].set_index("iso3")["exportaciones_usd"] / 1000     # a USD miles
X_w = totales_wb["WLD"]
X_j = mundo_oferta["valor_kusd"]
filas = []
for pais, iso in COMPARADORES.items():
    fila = exportadores[exportadores["pais"] == pais]
    if fila.empty or pd.isna(totales_wb.get(iso)):
        filas.append({"pais": pais, "nota": "sin dato en Trade Map o Banco Mundial"}); continue
    X_ij, X_i = fila.iloc[0]["valor_kusd"], totales_wb[iso]
    r = float(rca_balassa(X_ij, X_i, X_j, X_w))
    filas.append({"pais": pais, "X_ij_710391": X_ij, "X_i_total": X_i, "RCA": r, "RSCA": float(rsca_laursen(r)), "NRCA_x1e4": float(nrca(X_ij, X_i, X_j, X_w)) * 1e4})
vcr = pd.DataFrame(filas)
exportar(vcr, "g4_vcr_comparadores")
vcr
'''),
    code('''
vcr_cap71 = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA]})
vcr_cap71["RCA_cap71"] = rca_balassa(fila_canasta(canasta_co_exp, "71"), fila_canasta(canasta_co_exp, "TOTAL"),
                                     fila_canasta(canasta_mundo_exp, "71"), fila_canasta(canasta_mundo_exp, "TOTAL"))
vcr_cap71["RSCA_cap71"] = rsca_laursen(vcr_cap71["RCA_cap71"])
exportar(vcr_cap71, "g4_vcr_cap71")
fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
con_dato = vcr.dropna(subset=["RSCA"])
axes[0].bar(con_dato["pais"], con_dato["RSCA"], color=[NARANJA if p == "Colombia" else AZUL for p in con_dato["pais"]], width=0.55)
for x, (v, r) in enumerate(zip(con_dato["RSCA"], con_dato["RCA"])):
    axes[0].annotate(f"RSCA {v:+.2f}\\nRCA {r:.1f}", (x, v), textcoords="offset points", xytext=(0, 5 if v >= 0 else -24), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].axhline(0, color=GRIS_EJE, linewidth=0.8)
axes[0].set_ylim(-1.1, 1.3)
estilo(axes[0], f"RSCA en HS 710391, {ANIO_WB}", "Denominador: exportaciones de bienes y servicios (Banco Mundial)", eje_y="RSCA")
axes[1].plot(vcr_cap71["anio"], vcr_cap71["RCA_cap71"], color=VERDE, linewidth=2.2, marker="o", markersize=6)
for _, f in vcr_cap71.iterrows():
    axes[1].annotate(f"{f['RCA_cap71']:.2f}", (f["anio"], f["RCA_cap71"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].axhline(1, color=GRIS_EJE, linewidth=0.8, linestyle="--")
axes[1].set_xticks(vcr_cap71["anio"])
axes[1].set_ylim(0, vcr_cap71["RCA_cap71"].max() * 1.3)
estilo(axes[1], "RCA de Balassa del capítulo 71, Colombia", "Línea punteada = 1", "Trade Map (ITC), Banco Mundial (WDI), canasta HS2 del curso.", eje_y="RCA")
plt.tight_layout()
guardar(fig, "g4_vcr")
'''),
    analisis(),

    md("---\n# 6. Apertura comercial e IBCR de los mercados candidatos, 2020-2024\n\nCon los tres archivos del Banco Mundial del curso. La Unión Europea se toma como agregado (`EUU`). Emiratos Árabes Unidos no tiene dato de 2024 en esta versión de los WDI."),
    code('''
MERCADOS = {"EUU": "Unión Europea", "ARE": "Emiratos Árabes Unidos", "SGP": "Singapur", "CHE": "Suiza", "COL": "Colombia (referencia)"}
macro = (wb_pib.merge(wb_exp, on=["iso3", "pais", "anio"]).merge(wb_imp, on=["iso3", "pais", "anio"]))
macro = macro[macro["iso3"].isin(MERCADOS) & macro["anio"].between(2020, 2024)].copy()
macro["mercado"] = macro["iso3"].map(MERCADOS)
macro["apertura_pct"] = apertura_comercial(macro["exportaciones_usd"], macro["importaciones_usd"], macro["pib_usd"])
macro["IBCR"] = ibcr(macro["exportaciones_usd"], macro["importaciones_usd"])
tabla_macro = macro.pivot(index="anio", columns="mercado", values="apertura_pct")
exportar(macro[["mercado", "iso3", "anio", "pib_usd", "exportaciones_usd", "importaciones_usd", "apertura_pct", "IBCR"]], "g4_apertura_ibcr")
tabla_macro.round(1)
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
for color, mercado in zip(CATEGORIAS + [GRIS_MID], MERCADOS.values()):
    if mercado in tabla_macro.columns:
        axes[0].plot(tabla_macro.index, tabla_macro[mercado], color=color, linewidth=2.2, marker="o", markersize=5, label=mercado)
axes[0].set_xticks(tabla_macro.index)
axes[0].legend(frameon=False, fontsize=9)
estilo(axes[0], "Índice de apertura comercial", "(X + M) / PIB x 100", eje_y="%")
ultimo = macro.sort_values("anio").groupby("mercado").tail(1).set_index("mercado")
axes[1].bar(ultimo.index, ultimo["IBCR"], color=[ROJO if v < 0 else AZUL for v in ultimo["IBCR"]], width=0.55)
for x, (v, a) in enumerate(zip(ultimo["IBCR"], ultimo["anio"])):
    axes[1].annotate(f"{v:+.3f} ({a})", (x, v), textcoords="offset points", xytext=(0, 5 if v >= 0 else -12), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].axhline(0, color=GRIS_EJE, linewidth=0.8)
axes[1].set_ylim(-0.3, 0.3)
axes[1].tick_params(axis="x", labelsize=8)
estilo(axes[1], "IBCR de la economía completa, último año con dato", "(X - M) / (X + M)", "Banco Mundial (WDI), 2025.", eje_y="IBCR")
plt.tight_layout()
guardar(fig, "g4_apertura_ibcr")
'''),
    analisis("¿Qué dice la apertura de Singapur o Emiratos sobre su papel como hubs de reexportación?"),

    md("---\n# 7. Grubel-Lloyd del capítulo 71"),
    code('''
X71_2025 = separar_mundo(cap71_exp)[0]["valor_kusd"]
M71_2025 = separar_mundo(cap71_imp)[0]["valor_kusd"]
gl_2025 = float(grubel_lloyd(X71_2025, M71_2025))
print(f"Capitulo 71, 2025 (archivos del equipo): X = {X71_2025:,.0f}  M = {M71_2025:,.0f}  ->  GL = {gl_2025:.4f}")
gl_serie = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA],
                         "X_cap71": fila_canasta(canasta_co_exp, "71").values, "M_cap71": fila_canasta(canasta_co_imp, "71").values})
gl_serie["GL_cap71"] = grubel_lloyd(gl_serie["X_cap71"], gl_serie["M_cap71"])
gl_serie["IBCR_cap71"] = ibcr(gl_serie["X_cap71"], gl_serie["M_cap71"])
exportar(gl_serie, "g4_grubel_lloyd")
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(gl_serie["anio"], gl_serie["GL_cap71"], color=AZUL, linewidth=2.2, marker="o", markersize=6, label="Grubel-Lloyd")
ax.plot(gl_serie["anio"], gl_serie["IBCR_cap71"], color=VERDE, linewidth=2.2, marker="o", markersize=6, label="IBCR")
for _, f in gl_serie.iterrows():
    ax.annotate(f"{f['GL_cap71']:.3f}", (f["anio"], f["GL_cap71"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
ax.set_ylim(-0.1, 1.1)
ax.set_xticks(gl_serie["anio"])
ax.legend(frameon=False, fontsize=9, loc="center right")
estilo(ax, "Capítulo 71 en Colombia: Grubel-Lloyd e IBCR, 2021-2025", "GL: 0 = interindustrial puro, 1 = intraindustrial puro", "Trade Map (ITC), canasta HS2 del curso.", eje_y="índice")
guardar(fig, "g4_grubel_lloyd")
gl_serie
'''),
    analisis(),

    md("---\n# 8. Crecimiento de las importaciones y participación de Colombia en cada destino\n\n`cuota_en_socio_pct` = exportaciones de Colombia al destino / importaciones totales de HS 710391 del destino. `crec_importaciones_socio_5a_pct` es el crecimiento de esas importaciones totales."),
    code('''
mercados = destinos_2025.nlargest(15, "valor_kusd")[["pais", "valor_kusd", "cuota_en_socio_pct", "ranking_socio", "crec_valor_5a_pct", "crec_importaciones_socio_5a_pct"]]
exportar(mercados, "g4_mercados")
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
orden = mercados.dropna(subset=["cuota_en_socio_pct"]).sort_values("cuota_en_socio_pct")
axes[0].barh(orden["pais"], orden["cuota_en_socio_pct"], color=AZUL, height=0.6)
for y, (v, r) in enumerate(zip(orden["cuota_en_socio_pct"], orden["ranking_socio"])):
    axes[0].annotate(f"{v:.1f} % (n.º {r:.0f})", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(axes[0], "Cuota de Colombia en las importaciones de cada destino, 2025", "Quince mayores destinos", eje_x="%", rejilla="x")
puntos = mercados.dropna(subset=["cuota_en_socio_pct", "crec_importaciones_socio_5a_pct"])
tamanos = puntos["valor_kusd"] / puntos["valor_kusd"].max() * 900 + 40
axes[1].scatter(puntos["cuota_en_socio_pct"], puntos["crec_importaciones_socio_5a_pct"], s=tamanos, color=AZUL, alpha=0.55, edgecolor="white", linewidth=1.5)
for _, p in puntos.iterrows():
    axes[1].annotate(p["pais"], (p["cuota_en_socio_pct"], p["crec_importaciones_socio_5a_pct"]), textcoords="offset points", xytext=(6, 4), fontsize=8.5, color=GRIS_TEXT)
estilo(axes[1], "Cuota de Colombia frente al crecimiento de las importaciones del destino", "Tamaño = valor exportado por Colombia en 2025", "Trade Map (ITC), 2025.",
       eje_x="Cuota de Colombia (%)", eje_y="Crecimiento de las importaciones del destino, 5 años (%)")
plt.tight_layout()
guardar(fig, "g4_mercados")
mercados
'''),
    analisis(),

    md("---\n# 9. Ficha financiera de las comercializadoras (EMIS)\n\nLos tres reportes EMIS (`Esmeraldas de los Andes S A S.xlsx`, `Esmeraldas Mining Services S.A.S.xlsx`, `Esmeraldas Santa Rosa S.A.S.xlsx`) tienen restricción de redistribución y no están en el repositorio. En Colab, esta celda pide subirlos; si no los subes, la sección se salta y el resto del cuaderno funciona igual.\n\nTrampas del formato EMIS: un aviso legal en la primera fila, encabezados reales en la fila 10, varias tablas apiladas en la misma hoja (`Estado de Resultados`, `Balance General`...), cifras en **miles de COP** y un 2021 en ceros que en realidad es dato ausente."),
    code('''
def leer_emis_anual(ruta_archivo):
    """Extrae el Estado de Resultados de la hoja 'Anual' de un reporte EMIS. Devuelve formato largo en millones de COP."""
    hoja = pd.read_excel(ruta_archivo, sheet_name="Anual", header=None)
    empresa = str(hoja.iloc[2, 1]).strip()
    etiquetas = hoja.iloc[:, 1].astype(str).str.strip()
    inicio = etiquetas.index[etiquetas == "Estado de Resultados"][0]
    fin = etiquetas.index[(etiquetas == "Balance General") & (etiquetas.index > inicio)][0]
    anios = [str(c)[:4] for c in hoja.iloc[inicio, 2:7]]
    bloque = hoja.iloc[inicio + 2:fin, 1:7].copy()
    bloque.columns = ["cuenta"] + anios
    bloque = bloque.dropna(subset=["cuenta"])
    largo = bloque.melt(id_vars="cuenta", var_name="anio", value_name="miles_cop")
    largo["anio"] = largo["anio"].astype(int)
    largo["miles_cop"] = pd.to_numeric(largo["miles_cop"], errors="coerce").replace(0, np.nan)   # 0 = no reportado
    largo["millones_cop"] = largo["miles_cop"] / 1000
    largo.insert(0, "empresa", empresa)
    return largo

base_busqueda = RUTA_BASE if MODO == "local" else "/content"
archivos_emis = sorted(glob.glob(os.path.join(base_busqueda, "**", "Esmeraldas*.xlsx"), recursive=True))
if not archivos_emis and MODO == "github":
    from google.colab import files
    print("Sube los tres reportes EMIS (o cancela para saltar esta seccion).")
    files.upload()
    archivos_emis = sorted(glob.glob(os.path.join("/content", "**", "Esmeraldas*.xlsx"), recursive=True))

if archivos_emis:
    emis = pd.concat([leer_emis_anual(a) for a in archivos_emis], ignore_index=True)
    CUENTAS = ["Total Ingreso Operativo", "Ganancia operativa (EBIT)", "EBITDA", "Ganancia (Pérdida) Neta"]
    resumen_emis = emis[emis["cuenta"].isin(CUENTAS)].pivot_table(index=["empresa", "anio"], columns="cuenta", values="millones_cop")[CUENTAS]
    resumen_emis["margen_EBIT_pct"] = resumen_emis["Ganancia operativa (EBIT)"] / resumen_emis["Total Ingreso Operativo"] * 100
    exportar(resumen_emis.reset_index(), "g4_emis_resumen")
    display(resumen_emis.round(1))
else:
    emis = None
    print("No hay reportes EMIS disponibles: se salta la seccion.")
'''),
    code('''
if emis is not None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    empresas = resumen_emis.index.get_level_values("empresa").unique()
    for ax, (cuenta, titulo) in zip(axes, [("Total Ingreso Operativo", "Ingresos operativos"), ("Ganancia operativa (EBIT)", "EBIT"), ("margen_EBIT_pct", "Margen EBIT")]):
        for color, empresa in zip(CATEGORIAS, empresas):
            datos = resumen_emis.loc[empresa, cuenta].dropna()
            ax.plot(datos.index, datos.values, color=color, linewidth=2.2, marker="o", markersize=5, label=empresa)
        ax.set_xticks(range(2021, 2026))
        if cuenta != "margen_EBIT_pct":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.axhline(0, color=GRIS_EJE, linewidth=0.8)
        estilo(ax, titulo, "millones de COP" if cuenta != "margen_EBIT_pct" else "%", eje_y="")
    axes[0].legend(frameon=False, fontsize=8.5)
    fig.text(0.01, -0.03, "Fuente: EMIS (ISI Markets), reportes de empresa, 2026. Los ceros de 2021 se tratan como dato ausente.", fontsize=8, color=GRIS_EJE)
    plt.tight_layout()
    guardar(fig, "g4_emis")
'''),
    analisis("¿Qué dicen los márgenes sobre la capacidad de las comercializadoras para financiar una estrategia de valor agregado?"),

    md("---\n# 10. Tablero de decisión\n\nLa ficha cierra con un tablero que reúne todos los indicadores. La tabla siguiente los junta tal como quedaron calculados arriba; el equipo la completa con la columna de **señal** y **decisión** de su cadena interpretativa (DATO → CÁLCULO → INDICADOR → INTERPRETACIÓN → SEÑAL → DECISIÓN)."),
    code('''
ultimo = concentracion.iloc[-1]
tablero = pd.DataFrame([
    {"dimension": "Concentración", "indicador": "HHI destinos 2025", "valor": ultimo["HHI"]},
    {"dimension": "Concentración", "indicador": "Theil destinos 2025", "valor": ultimo["Theil"]},
    {"dimension": "Concentración", "indicador": "Número equivalente de destinos 2025", "valor": ultimo["numero_equivalente"]},
    {"dimension": "Participación", "indicador": f"Participación del mayor destino 2025 ({participacion.iloc[0]['pais']}) %", "valor": participacion.iloc[0]["participacion_pct"]},
    {"dimension": "Desempeño", "indicador": "CAGR exportaciones 2016-2025 %", "valor": cagr(total[2016], total[2025], 9)},
    {"dimension": "Competitividad", "indicador": "RCA Colombia HS 710391", "valor": vcr.set_index("pais").loc["Colombia", "RCA"]},
    {"dimension": "Competitividad", "indicador": "RSCA Colombia HS 710391", "valor": vcr.set_index("pais").loc["Colombia", "RSCA"]},
    {"dimension": "Competitividad", "indicador": "RCA Colombia capítulo 71, 2025", "valor": vcr_cap71.iloc[-1]["RCA_cap71"]},
    {"dimension": "Estructura", "indicador": "Grubel-Lloyd capítulo 71, 2025", "valor": gl_2025},
    {"dimension": "Mercados", "indicador": "Cuota de Colombia en su mayor destino %", "valor": mercados.iloc[0]["cuota_en_socio_pct"]},
])
tablero["senal"] = ""
tablero["decision"] = ""
exportar(tablero, "g4_tablero")
tablero
'''),
    analisis("Complete las columnas de señal y decisión para cada indicador."),

    cierre([REF_BALASSA, REF_YU, REF_GL, REF_WB]),
]

escribir(celdas, NB)
