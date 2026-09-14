from comun import *

G = "Proyectos finales/Grupo 6"
A = G + "/datos/Anexo_Datos_Curuba_Equipo6/"
G1 = "Proyectos finales/Grupo 1/datos/"
NB = G + "/Grupo_6_Curuba.ipynb"

ARCHIVOS = {
    "t2_largo":   A + "03_datos_limpios/t2_exportadores_081090_largo.csv",
    "t3_mundo":   A + "03_datos_limpios/t3_mundo_081090.csv",
    "c1_produccion": A + "03_datos_limpios/c1_produccion_curuba.csv",
    "c2_derivados":  A + "03_datos_limpios/c2_produccion_derivados.csv",
    "d1_flujos":  A + "03_datos_limpios/d1_flujos_pais_081090.csv",
    "i4_matriz":  A + "05_indicadores_equipo/i4_matriz_multicriterio.csv",
    "r6_cobertura": A + "04_indicadores_reales/r6_cobertura_y_calidad.csv",
    "exp_serie_destinos": G1 + "colombias-exports-to-world-by-importer_081090.csv",
    "imp_2025_xlsx":      G1 + "colombias-imports-from-world-in-2025-by-exporter_081090.xlsx",
    "wb_pib": "data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_234.csv",
    "wb_exp": "data/API_NE.EXP.GNFS.CD_DS2_en_csv_v2_35140.csv",
    "wb_imp": "data/API_NE.IMP.GNFS.CD_DS2_en_csv_v2_33330.csv",
    "canasta_co_exp":    "data/co_exp_productos_hs2_serie.xls",
    "canasta_co_imp":    "data/co_imp_productos_hs2_serie.csv",
    "canasta_mundo_exp": "data/mundo_exp_productos_hs2_serie.csv",
}

METR = [
    ("Oferta mundial de HS 081090", "¿Quién exporta, cuánto crece cada uno y dónde están Colombia, Ecuador y Perú?"),
    ("HHI de la oferta mundial", "¿El mercado mundial se concentra o se fragmenta?"),
    ("IBCR, IAC y CE", "¿Qué economías son mercados de consumo y cuáles hubs de reexportación?"),
    ("HHI, Theil y Grubel-Lloyd de Colombia", "¿Qué tan dispersos están los destinos colombianos y qué tipo de comercio es?"),
    ("Balassa, RSCA y Lafay", "¿Colombia, Ecuador y Perú tienen ventaja revelada en esta subpartida?"),
    ("Matriz multicriterio", "¿Qué mercado prioriza la estrategia de entrada y qué tan sensible es a los pesos?"),
    ("Sensibilidad al factor de imputación", "¿Cuánto cambian las cifras de curuba si el 3,8 % fuera 12,5 %?"),
]

celdas = [
    badge(NB),
    portada("Grupo 6. Curuba fresca: estrategia de entrada concentrada en uno o dos mercados prioritarios",
            "Grupo 6", "Curuba (*Passiflora mollissima*), NANDINA 0810.90.10.40. En Trade Map solo existe **HS 081090**, que agrupa curuba con maracuyá, pitahaya y otros; el equipo usa un factor de imputación del 3,8 % para aislarla.",
            "¿Cómo puede una empresa exportadora colombiana de curuba fresca diseñar una estrategia de entrada que concentre su oferta en uno o dos mercados prioritarios, apoyada en un manejo poscosecha que garantice la calidad durante el trayecto logístico?",
            METR, "*Equipo 6 — Ficha técnica del estudio: metodología y plan de minería de datos* y su paquete `Anexo_Datos_Curuba_Equipo6`. Como el paquete separa **datos reales de Trade Map** de **estimaciones del equipo**, este cuaderno marca en cada sección cuál de las dos capas usa. La vista por destino de HS 081090 y los datos del Banco Mundial, pendientes en el plan del equipo, se tomaron de la carpeta del grupo 1 y de `data/` del curso."),
    md("---\n# 0. Preparación del entorno"),
    CELL_IMPORTS,
    cell_config(G, ARCHIVOS),
    CELL_DESCARGA,
    CELL_LECTORES,
    cell_metricas(["hhi", "cr", "theil", "gl", "ibcr", "apertura", "ce", "rca", "lafay", "cagr", "multicriterio"]),

    md("---\n# 1. Los datos\n\n**Capa real (Trade Map):** `t2` exportadores mundiales de HS 081090 2016-2025 en formato largo, `t3` el total mundial, `r6` la cobertura por año; la serie de Colombia por destino y sus importaciones 2025 (carpeta del grupo 1). **Capa del equipo:** `c1`/`c2` producción de pasifloras y curuba con la imputación del 3,8 %, `d1` flujos por país estimados, `i4` matriz multicriterio. **Curso:** Banco Mundial y canasta HS2.\n\nRecordatorio de su ficha metodológica: los códigos de economía se leen como texto (`040` no es `40`), una celda vacía no es cero, y para rankings definitivos conviene 2024 (cobertura 86,9 %) y no 2025 (68,1 %)."),
    code('''
t2 = pd.read_csv(ruta("t2_largo"), dtype={"codigo_tm": str})
t3 = pd.read_csv(ruta("t3_mundo")).set_index("anio")["exportaciones_mundiales_usd_miles"]
r6 = pd.read_csv(ruta("r6_cobertura"))
c1 = pd.read_csv(ruta("c1_produccion")).set_index("metrica")
c2 = pd.read_csv(ruta("c2_derivados"))
d1 = pd.read_csv(ruta("d1_flujos"))
i4 = pd.read_csv(ruta("i4_matriz"))
serie_destinos = leer_serie_trademap(ruta("exp_serie_destinos"))
imp_2025 = limpiar_trademap(pd.read_excel(ruta("imp_2025_xlsx"), dtype={"reporterCd": str, "partnerCd": str, "productCd": str}))
wb_pib = leer_banco_mundial(ruta("wb_pib"), "pib_usd")
wb_exp = leer_banco_mundial(ruta("wb_exp"), "exportaciones_usd")
wb_imp = leer_banco_mundial(ruta("wb_imp"), "importaciones_usd")
canasta_co_exp, canasta_co_imp, canasta_mundo_exp = (leer_canasta(ruta(k)) for k in ("canasta_co_exp", "canasta_co_imp", "canasta_mundo_exp"))

print(f"t2: {t2['pais'].nunique()} economias x {t2['anio'].nunique()} anios; celdas vacias (no reportado): {t2['exportaciones_usd_miles'].isna().sum()}")
display(r6)
c1
'''),

    md("---\n# 2. Oferta mundial de HS 081090: series, cuotas y CAGR *(capa real)*"),
    code('''
FOCO = ["Colombia", "Ecuador", "Perú"]
GRANDES = ["Viet Nam", "Tailandia", "Países Bajos"]
ANIO_RANKING = 2024      # el recomendado por la ficha metodologica del equipo
t2a = t2.dropna(subset=["exportaciones_usd_miles"])
cuotas = t2a.merge(t3.rename("mundo"), left_on="anio", right_index=True)
cuotas["cuota_pct"] = cuotas["exportaciones_usd_miles"] / cuotas["mundo"] * 100
cuotas["puesto"] = cuotas.groupby("anio")["exportaciones_usd_miles"].rank(ascending=False, method="min").astype(int)
ancho = t2a.pivot(index="anio", columns="pais", values="exportaciones_usd_miles")
resumen = (cuotas[cuotas["anio"] == ANIO_RANKING].nlargest(10, "exportaciones_usd_miles")[["pais", "exportaciones_usd_miles", "cuota_pct", "puesto"]])
resumen = pd.concat([resumen, cuotas[(cuotas["anio"] == ANIO_RANKING) & cuotas["pais"].isin(FOCO)][resumen.columns]]).drop_duplicates("pais")
resumen["cagr_2016_%d_pct" % ANIO_RANKING] = [cagr(ancho.loc[2016, p], ancho.loc[ANIO_RANKING, p], ANIO_RANKING - 2016) for p in resumen["pais"]]
exportar(resumen, "g6_oferta_mundial")
resumen
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))
for color, pais in zip(CATEGORIAS[:3], FOCO):
    axes[0].plot(ancho.index, ancho[pais], color=color, linewidth=2.4, marker="o", markersize=5, label=pais)
for pais in GRANDES:
    axes[0].plot(ancho.index, ancho[pais], color=GRIS_MID, linewidth=1.6, linestyle="--", label=pais)
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
axes[0].set_xticks(ancho.index)
axes[0].legend(frameon=False, fontsize=8.5, ncol=2)
estilo(axes[0], "Exportaciones de HS 081090 por economía, 2016-2025", "USD; los andinos en color, los tres grandes en gris", eje_y="USD")
orden = resumen.sort_values("cuota_pct")
colores = [NARANJA if p == "Colombia" else (AZUL if p in FOCO else GRIS_MID) for p in orden["pais"]]
axes[1].barh(orden["pais"], orden["cuota_pct"], color=colores, height=0.6)
for y, (v, pu) in enumerate(zip(orden["cuota_pct"], orden["puesto"])):
    axes[1].annotate(f"{v:.1f} %  (n.º {pu})", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(axes[1], f"Cuota en la oferta mundial, {ANIO_RANKING}", "Diez mayores exportadores más Colombia, Ecuador y Perú", "Trade Map (ITC) vía paquete del equipo 6.", eje_x="%", rejilla="x")
plt.tight_layout()
guardar(fig, "g6_oferta_mundial")
'''),
    code('''
puestos = cuotas[cuotas["pais"].isin(FOCO)].pivot(index="anio", columns="pais", values="puesto")[FOCO]
fig, ax = plt.subplots(figsize=(9, 4.4))
for color, pais in zip(CATEGORIAS[:3], FOCO):
    ax.plot(puestos.index, puestos[pais], color=color, linewidth=2.4, marker="o", markersize=6, label=pais)
    ax.annotate(f"{pais} n.º {puestos[pais].iloc[-1]}", (puestos.index[-1], puestos[pais].iloc[-1]), textcoords="offset points", xytext=(8, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.invert_yaxis()
ax.set_xticks(puestos.index)
ax.set_xlim(2016, 2027)
ax.legend(frameon=False, fontsize=9, loc="lower left")
estilo(ax, "Puesto en el ranking mundial de exportadores de HS 081090", "1 = mayor exportador", "Trade Map (ITC) vía paquete del equipo 6.", eje_y="puesto")
guardar(fig, "g6_ranking")
exportar(puestos.reset_index(), "g6_ranking")
'''),
    analisis("La ficha describe a Ecuador y Perú como competidores con ventaja incipiente. ¿Qué muestran los datos reales?"),

    md("---\n# 3. HHI de la oferta mundial *(capa real)*"),
    code('''
hhi_mundial = (t2a.groupby("anio")["exportaciones_usd_miles"]
               .agg(HHI=hhi, CR5=lambda v: cr_n(v, 5), economias=lambda v: int((v > 0).sum())).reset_index())
hhi_mundial["numero_equivalente"] = numeros_equivalentes(hhi_mundial["HHI"])
exportar(hhi_mundial, "g6_hhi_mundial")
fig, ax = plt.subplots(figsize=(9, 4.4))
ax.plot(hhi_mundial["anio"], hhi_mundial["HHI"], color=AZUL, linewidth=2.4, marker="o", markersize=7)
for _, f in hhi_mundial.iterrows():
    ax.annotate(f"{f['HHI']:.3f}", (f["anio"], f["HHI"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
ax.axhspan(0.18, 1, color=ROJO, alpha=0.06)
ax.axhspan(0.15, 0.18, color=NARANJA, alpha=0.06)
ax.set_ylim(0, 0.3)
ax.set_xticks(hhi_mundial["anio"])
estilo(ax, "HHI de la oferta mundial de HS 081090, 2016-2025", "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", "Trade Map (ITC) vía paquete del equipo 6.", eje_y="HHI")
guardar(fig, "g6_hhi_mundial")
hhi_mundial
'''),
    analisis(),

    md("---\n# 4. Posición comercial: IBCR, IAC y CE\n\nDos cálculos en paralelo. **(a)** Con las cifras de `d1` y `c1`, que son estimaciones del equipo. **(b)** IAC e IBCR de la economía completa de las seis economías con el Banco Mundial (capa real del curso). El coeficiente de exportación necesita el **valor** de la producción de curuba, que no está en el paquete: la celda tiene un parámetro editable de precio al productor para calcularlo."),
    code('''
# (a) estimaciones del equipo
d1["IBCR_recalculado"] = ibcr(d1["exportaciones_X_usd_miles"], d1["importaciones_M_usd_miles"])
d1["GL_recalculado"] = grubel_lloyd(d1["exportaciones_X_usd_miles"], d1["importaciones_M_usd_miles"])
tabla_a = d1[["pais", "exportaciones_X_usd_miles", "importaciones_M_usd_miles", "IBCR_calculado", "IBCR_recalculado", "IAC_pct", "GL_recalculado", "clasificacion_comercial"]]
exportar(tabla_a, "g6_posicion_equipo")
tabla_a
'''),
    code('''
# (b) Banco Mundial, economia completa, 2020-2024
ECONOMIAS = {"COL": "Colombia", "NLD": "Países Bajos", "DEU": "Alemania", "ESP": "España", "CAN": "Canadá", "ARE": "Emiratos Árabes Unidos"}
macro = wb_pib.merge(wb_exp, on=["iso3", "pais", "anio"]).merge(wb_imp, on=["iso3", "pais", "anio"])
macro = macro[macro["iso3"].isin(ECONOMIAS) & macro["anio"].between(2020, 2024)].copy()
macro["economia"] = macro["iso3"].map(ECONOMIAS)
macro["IAC_pct"] = apertura_comercial(macro["exportaciones_usd"], macro["importaciones_usd"], macro["pib_usd"])
macro["IBCR"] = ibcr(macro["exportaciones_usd"], macro["importaciones_usd"])
ultimo = macro.dropna(subset=["IAC_pct"]).sort_values("anio").groupby("economia").tail(1).set_index("economia").reindex(ECONOMIAS.values())
exportar(macro[["economia", "iso3", "anio", "pib_usd", "exportaciones_usd", "importaciones_usd", "IAC_pct", "IBCR"]], "g6_posicion_banco_mundial")
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
axes[0].bar(ultimo.index, ultimo["IAC_pct"], color=[NARANJA if e == "Colombia" else AZUL for e in ultimo.index], width=0.55)
for x, (v, a) in enumerate(zip(ultimo["IAC_pct"], ultimo["anio"])):
    axes[0].annotate(f"{v:.0f} % ({a:.0f})", (x, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].tick_params(axis="x", labelsize=8)
estilo(axes[0], "Índice de apertura comercial, economía completa", "(X + M) / PIB x 100, último año con dato", eje_y="%")
axes[1].bar(ultimo.index, ultimo["IBCR"], color=[ROJO if v < 0 else AZUL for v in ultimo["IBCR"]], width=0.55)
for x, v in enumerate(ultimo["IBCR"]):
    axes[1].annotate(f"{v:+.3f}", (x, v), textcoords="offset points", xytext=(0, 4 if v >= 0 else -12), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].axhline(0, color=GRIS_EJE, linewidth=0.8)
axes[1].set_ylim(-0.25, 0.25)
axes[1].tick_params(axis="x", labelsize=8)
estilo(axes[1], "IBCR de la economía completa", "(X - M) / (X + M)", "Banco Mundial (WDI), 2025.", eje_y="IBCR")
plt.tight_layout()
guardar(fig, "g6_posicion_banco_mundial")
ultimo[["anio", "IAC_pct", "IBCR"]]
'''),
    code('''
# Coeficiente de exportacion de la curuba: CE = X / valor de la produccion x 100
# ====================== EDITABLE ======================
PRECIO_PRODUCTOR_USD_T = np.nan        # precio promedio al productor en USD por tonelada (Agronet / SIPSA). Ej.: 900
# ======================================================
produccion_t = c1.loc["Produccion estimada de curuba (ton)"]
exportado = c1.loc["Valor exportado imputado 3.8% (USD miles)"]
if pd.notna(PRECIO_PRODUCTOR_USD_T):
    valor_produccion_kusd = produccion_t * PRECIO_PRODUCTOR_USD_T / 1000
    ce = pd.DataFrame({"anio": produccion_t.index.astype(int), "produccion_t": produccion_t.values, "valor_produccion_kusd": valor_produccion_kusd.values,
                       "exportado_kusd": exportado.values, "CE_pct": coeficiente_exportacion(exportado.values, valor_produccion_kusd.values)})
    exportar(ce, "g6_coeficiente_exportacion")
    display(ce)
else:
    print("Escribe PRECIO_PRODUCTOR_USD_T para calcular el coeficiente de exportacion.")
'''),
    analisis("¿Qué economías se comportan como hubs (IAC alto, IBCR cerca de cero) y cuáles como consumo final?"),

    md("---\n# 5. Colombia: concentración de destinos (HHI, Theil) y Grubel-Lloyd *(capa real, HS 081090 agregado)*\n\nLa vista por país socio que el plan del equipo marcaba como pendiente. Aplica al agregado HS 081090, no a la curuba sola."),
    code('''
paises_destino = serie_destinos[serie_destinos["codigo"] != "000"]
concentracion = (paises_destino.groupby("anio")["valor_kusd"]
                 .agg(HHI=hhi, Theil=theil, CR3=lambda v: cr_n(v, 3), destinos_activos=lambda v: int((v > 0).sum())).reset_index())
concentracion["numero_equivalente"] = numeros_equivalentes(concentracion["HHI"])
X_2025 = serie_destinos[(serie_destinos["codigo"] == "000") & (serie_destinos["anio"] == 2025)]["valor_kusd"].iloc[0]
M_2025 = separar_mundo(imp_2025)[0]["valor_kusd"]
print(f"Colombia 2025, HS 081090: X = {X_2025:,.0f}  M = {M_2025:,.0f}  ->  IBCR = {float(ibcr(X_2025, M_2025)):+.3f}   GL = {float(grubel_lloyd(X_2025, M_2025)):.3f}")
print(f"Comparar con la ficha del equipo: HHI curuba 0,0842 | Theil 1,845 | GL 0,021 (estimados con imputacion)")
exportar(concentracion, "g6_concentracion_destinos")
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
estilo(axes[0], "HHI de destinos de Colombia, HS 081090", "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", eje_y="HHI")
destinos_2025 = paises_destino[paises_destino["anio"] == 2025].nlargest(10, "valor_kusd").copy()
destinos_2025["participacion_pct"] = destinos_2025["valor_kusd"] / X_2025 * 100
orden = destinos_2025.sort_values("participacion_pct")
axes[1].barh(orden["pais"], orden["participacion_pct"], color=AZUL, height=0.6)
for y, v in enumerate(orden["participacion_pct"]):
    axes[1].annotate(f"{v:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(axes[1], "Participación por destino, 2025", f"Theil 2025 = {concentracion.iloc[-1]['Theil']:.2f}; número equivalente = {concentracion.iloc[-1]['numero_equivalente']:.1f}", "Trade Map (ITC), 2025.", eje_x="%", rejilla="x")
plt.tight_layout()
guardar(fig, "g6_concentracion_destinos")
'''),
    analisis("El HHI real del agregado 081090 y el HHI de curuba publicado en la ficha cuentan historias opuestas. ¿Cuál sostiene la estrategia de concentrar en uno o dos mercados?"),

    md("---\n# 6. Ventaja comparativa: Balassa, RSCA y Lafay\n\n**Colombia, capítulo 08 (2021-2025):** con la canasta del curso. **Colombia, Ecuador y Perú en HS 081090:** numerador de Trade Map (`t2`, `t3`), denominador con exportaciones de bienes y servicios del Banco Mundial (aproximación). **Lafay:** sobre los 97 capítulos de Colombia, resaltando el 08."),
    code('''
ANIO_VCR = 2024
X_j = t3[ANIO_VCR]
totales_wb = wb_exp[wb_exp["anio"] == ANIO_VCR].set_index("iso3")["exportaciones_usd"] / 1000
X_w = totales_wb["WLD"]
filas = []
for pais, iso in {"Colombia": "COL", "Ecuador": "ECU", "Perú": "PER"}.items():
    X_ij, X_i = ancho.loc[ANIO_VCR, pais], totales_wb[iso]
    r = float(rca_balassa(X_ij, X_i, X_j, X_w))
    filas.append({"pais": pais, "X_ij_081090": X_ij, "X_i_total": X_i, "RCA": r, "RSCA": float(rsca_laursen(r))})
vcr = pd.DataFrame(filas)
vcr_cap08 = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA]})
vcr_cap08["RCA_cap08"] = rca_balassa(fila_canasta(canasta_co_exp, "08"), fila_canasta(canasta_co_exp, "TOTAL"), fila_canasta(canasta_mundo_exp, "08"), fila_canasta(canasta_mundo_exp, "TOTAL"))
vcr_cap08["RSCA_cap08"] = rsca_laursen(vcr_cap08["RCA_cap08"])
print("Comparar con la ficha: RCA curuba 12,45 / RSCA 0,851 (estimados con imputacion)")
exportar(vcr, "g6_vcr_andinos"); exportar(vcr_cap08, "g6_vcr_cap08")
display(vcr); vcr_cap08
'''),
    code('''
capitulos = canasta_co_exp[canasta_co_exp["codigo"] != "TOTAL"][["codigo", "producto", "2025"]].rename(columns={"2025": "X"})
capitulos = capitulos.merge(canasta_co_imp[["codigo", "2025"]].rename(columns={"2025": "M"}), on="codigo")
capitulos["LFI"] = lafay(capitulos["X"], capitulos["M"])
capitulos["producto"] = capitulos["producto"].str.slice(0, 40)
ranking_lafay = capitulos.sort_values("LFI", ascending=False).reset_index(drop=True)
exportar(ranking_lafay, "g6_lafay")
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
axes[0].bar(vcr["pais"], vcr["RSCA"], color=[NARANJA if p == "Colombia" else AZUL for p in vcr["pais"]], width=0.5)
for x, (v, r) in enumerate(zip(vcr["RSCA"], vcr["RCA"])):
    axes[0].annotate(f"RSCA {v:+.2f}\\nRCA {r:.1f}", (x, v), textcoords="offset points", xytext=(0, 5 if v >= 0 else -24), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].axhline(0, color=GRIS_EJE, linewidth=0.8)
axes[0].set_ylim(-1.1, 1.3)
estilo(axes[0], f"RSCA en HS 081090, {ANIO_VCR}", "Denominador: exportaciones de bienes y servicios (Banco Mundial)", eje_y="RSCA")
extremos = pd.concat([ranking_lafay.head(8), ranking_lafay.tail(4)]).sort_values("LFI")
colores = [NARANJA if c == "08" else (AZUL if v >= 0 else ROJO) for c, v in zip(extremos["codigo"], extremos["LFI"])]
axes[1].barh(extremos["codigo"] + "  " + extremos["producto"], extremos["LFI"], color=colores, height=0.6)
axes[1].axvline(0, color=GRIS_EJE, linewidth=0.8)
axes[1].tick_params(axis="y", labelsize=8)
estilo(axes[1], "Índice de Lafay por capítulo HS2, Colombia 2025", "Ocho mayores y cuatro menores; capítulo 08 resaltado", "Trade Map (ITC), Banco Mundial, canasta HS2 del curso.", eje_x="LFI", rejilla="x")
plt.tight_layout()
guardar(fig, "g6_vcr")
'''),
    analisis(),

    md("---\n# 7. Matriz multicriterio *(capa del equipo, editable)*\n\nLos cinco criterios y pesos de la ficha (30/25/20/15/10) con los puntajes 1-5 del equipo, tal como están en `i4`. Cambia pesos o puntajes y vuelve a ejecutar; la prueba de sensibilidad mueve cada peso ±5 puntos."),
    code('''
criterios = i4[i4["criterio"].str.match(r"^\\d")].copy()
MERCADOS = [c for c in criterios.columns if c not in ("criterio", "peso")]
# ====================== EDITABLE ======================
PESOS = dict(zip(criterios["criterio"], criterios["peso"] * 100))
PUNTAJES = criterios.set_index("criterio")[MERCADOS].astype(float)
# ======================================================
matriz = matriz_multicriterio(PUNTAJES, PESOS)
exportar(matriz.reset_index().rename(columns={"index": "mercado"}), "g6_matriz_multicriterio")
matriz.round(2)
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={"width_ratios": [1.3, 1]})
im = axes[0].imshow(PUNTAJES.values, cmap="Blues", vmin=1, vmax=5, aspect="auto")
axes[0].set_xticks(range(len(MERCADOS))); axes[0].set_xticklabels(MERCADOS, fontsize=9)
axes[0].set_yticks(range(len(PUNTAJES))); axes[0].set_yticklabels([f"{c}  ({PESOS[c]:.0f} %)" for c in PUNTAJES.index], fontsize=9)
for i in range(PUNTAJES.shape[0]):
    for j in range(PUNTAJES.shape[1]):
        v = PUNTAJES.iloc[i, j]
        axes[0].text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=9, color="white" if v >= 4 else TINTA)
axes[0].set_title("Puntajes 1-5 por criterio y mercado (peso entre paréntesis)", fontsize=13, color=TINTA, loc="left", pad=14)
axes[0].tick_params(colors=GRIS_EJE)
for lado in axes[0].spines.values(): lado.set_visible(False)
acumulado = np.zeros(len(matriz))
for color, criterio in zip(CATEGORIAS + [GRIS_MID], PESOS.keys()):
    axes[1].barh(matriz.index, matriz[criterio], left=acumulado, color=color, height=0.6, label=criterio.split(". ", 1)[-1], edgecolor="white", linewidth=1.5)
    acumulado += matriz[criterio].values
for y, t in enumerate(matriz["Total"]):
    axes[1].annotate(f"{t:.2f}", (t, y), textcoords="offset points", xytext=(5, 0), va="center", fontsize=9, color=GRIS_TEXT)
axes[1].invert_yaxis()
axes[1].set_xlim(0, 5.6)
leyenda_fuera(axes[1])
estilo(axes[1], "Puntaje ponderado (máximo 5)", "Contribución de cada criterio", "Ficha técnica del equipo 6 (matriz i4).", eje_x="Puntaje", rejilla="x")
plt.tight_layout()
guardar(fig, "g6_matriz_multicriterio")
'''),
    code('''
def sensibilidad(puntajes, pesos, delta=5):
    base = matriz_multicriterio(puntajes, pesos).index.tolist()
    filas = []
    for criterio in pesos:
        for signo in (+delta, -delta):
            alterados = dict(pesos); alterados[criterio] = max(0, alterados[criterio] + signo)
            orden = matriz_multicriterio(puntajes, alterados).index.tolist()
            filas.append({"peso_modificado": criterio, "cambio": f"{signo:+d}", "primero": orden[0], "segundo": orden[1],
                          "cambia_el_lider": orden[0] != base[0], "cambia_el_orden": orden != base})
    return pd.DataFrame(filas)
prueba = sensibilidad(PUNTAJES, PESOS)
print("Orden base:", " > ".join(matriz.index))
print(f"El líder cambia en {prueba['cambia_el_lider'].sum()} de {len(prueba)} escenarios; el orden completo cambia en {prueba['cambia_el_orden'].sum()}.")
exportar(prueba, "g6_sensibilidad_pesos")
prueba
'''),
    analisis("¿Los dos mercados prioritarios resisten cambios razonables en los pesos? ¿Qué criterio tiene datos y cuál es juicio experto?"),

    md("---\n# 8. Sensibilidad al factor de imputación *(capa del equipo)*\n\nEl paquete imputa la curuba como el 3,8 % de la base comercial regional, pero la participación productiva real de la curuba en las pasifloras es de 12,5 % (hoja `c2`). Esta celda recalcula el valor imputado con ambos factores y lo compara con las exportaciones reales de Colombia en HS 081090."),
    code('''
# ====================== EDITABLE ======================
FACTORES = {"3,8 % (ficha)": 0.038, "12,5 % (participación productiva)": c2["participacion_curuba_en_pasifloras_pct"].mean() / 100}
# ======================================================
base_regional = c2.set_index("anio")["base_comercio_america_latina_usd_miles"]
exportaciones_reales = serie_destinos[serie_destinos["codigo"] == "000"].set_index("anio")["valor_kusd"]
sens = pd.DataFrame({nombre: base_regional * f for nombre, f in FACTORES.items()})
sens["Colombia exporta HS 081090 (real)"] = exportaciones_reales.reindex(sens.index)
for nombre in FACTORES:
    sens[f"{nombre} como % del 081090 real"] = sens[nombre] / sens["Colombia exporta HS 081090 (real)"] * 100
exportar(sens.reset_index(), "g6_sensibilidad_factor")
fig, ax = plt.subplots(figsize=(9, 4.6))
for color, nombre in zip([AZUL, NARANJA], FACTORES):
    ax.plot(sens.index, sens[nombre], color=color, linewidth=2.2, marker="o", markersize=5, label=f"Curuba imputada al {nombre}")
ax.plot(sens.index, sens["Colombia exporta HS 081090 (real)"], color=GRIS_EJE, linewidth=1.6, linestyle="--", label="HS 081090 real (Trade Map)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
ax.set_xticks(sens.index)
ax.legend(frameon=False, fontsize=9)
estilo(ax, "Valor exportado de curuba según el factor de imputación", "USD; contra las exportaciones reales del agregado HS 081090", "Paquete del equipo 6 y Trade Map (ITC).", eje_y="USD")
guardar(fig, "g6_sensibilidad_factor")
sens.round(1)
'''),
    analisis("¿Qué factor es más defendible y cómo cambia la lectura de todos los indicadores de la capa del equipo?"),

    cierre([REF_BALASSA, REF_LAFAY, REF_GL, REF_WB, REF_BAENA]),
]

escribir(celdas, NB)
