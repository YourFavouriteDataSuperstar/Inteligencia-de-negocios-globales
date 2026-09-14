from comun import *

G = "Proyectos finales/Grupo 7"
D = G + "/datos/Datos_proyectobrief/"
NB = G + "/Grupo_7_Rosas.ipynb"

ARCHIVOS = {
    "exp_serie":  D + "colombias-exports-to-world-by-importer_060311.csv",
    "exp_2025":   D + "colombias-exports-to-world-in-2025-by-importer_060311.csv",
    "exp_all":    D + "colombias-exports-to-world-in-2025-by-importer_all.csv",
    "imp_2025":   D + "colombias-imports-from-world-in-2025-by-exporter_060311.csv",
    "imp_all":    D + "colombias-imports-from-world-in-2025-by-exporter_all.csv",
    "mundo_exp":  D + "exporting-countries-in-2025_060311.csv",
    "canasta_co_exp":    "data/co_exp_productos_hs2_serie.xls",
    "canasta_co_imp":    "data/co_imp_productos_hs2_serie.csv",
    "canasta_mundo_exp": "data/mundo_exp_productos_hs2_serie.csv",
}

METR = [
    ("Series por destino y CAGR", "¿Hacia dónde van las rosas colombianas y cómo ha cambiado en diez años?"),
    ("HHI y CR3 de destinos", "¿De cuántos mercados depende realmente la rosa colombiana?"),
    ("Balanza Comercial Relativa (BCR)", "¿Colombia es exportador neto puro de rosas?"),
    ("Participación de mercado por destino", "¿Qué porción de las importaciones de rosas de cada destino es colombiana?"),
    ("Valor unitario (USD/t)", "¿A qué precio implícito vende Colombia frente a sus competidores y en cada destino?"),
    ("Cuota en la oferta mundial", "¿Qué lugar ocupa Colombia entre los exportadores de rosas?"),
    ("RCA, RSCA y NRCA", "¿Colombia exporta proporcionalmente más rosas que el resto del mundo?"),
    ("Índice de Lafay", "¿Las rosas van mejor que el promedio comercial de Colombia?"),
    ("Matriz de decisión 0-100 con sensibilidad", "¿Qué mercado priorizar, y qué tan robusta es esa respuesta?"),
]

celdas = [
    badge(NB),
    portada("Grupo 7. Rosa Freedom: inteligencia comercial para priorizar mercados de exportación",
            "Grupo 7", "Rosas frescas cortadas, **HS 060311** (la variedad Freedom no se separa en las estadísticas; los indicadores se leen a nivel de categoría, como advierte la ficha)",
            "¿Qué mercados de destino ofrecen la mejor combinación entre ventaja comparativa revelada, participación y crecimiento de la demanda, especialización exportadora y riesgo controlable para la Rosa Freedom colombiana?",
            METR, "*Equipo 7 — Ficha técnica del estudio* (septiembre de 2026)"),
    md("---\n# 0. Preparación del entorno"),
    CELL_IMPORTS,
    cell_config(G, ARCHIVOS),
    CELL_DESCARGA,
    CELL_LECTORES,
    cell_metricas(["hhi", "cr", "ibcr", "rca", "nrca", "lafay", "cagr", "multicriterio"]),

    md("---\n# 1. Los datos\n\nSeis descargas de Trade Map del equipo (HS 060311 y el total de todos los productos) y tres archivos del curso con la canasta por capítulo HS2, que aportan los totales mundiales que faltaban para Balassa y Lafay."),
    code('''
serie = leer_serie_trademap(ruta("exp_serie"))              # Colombia exporta rosas, por destino, 2016-2025
exp_2025 = leer_trademap(ruta("exp_2025"))                  # lo mismo, corte 2025 con indicadores
exp_all  = leer_trademap(ruta("exp_all"))                   # Colombia exporta TODO, por destino, 2025
imp_2025 = leer_trademap(ruta("imp_2025"))                  # Colombia importa rosas, por origen, 2025
imp_all  = leer_trademap(ruta("imp_all"))                   # Colombia importa TODO, 2025
mundo_exp = leer_trademap(ruta("mundo_exp"))                # exportadores mundiales de rosas, 2025

mundo_2025, destinos_2025 = separar_mundo(exp_2025)
mundo_oferta, exportadores = separar_mundo(mundo_exp)

print(f"Colombia exporto rosas por USD {mundo_2025['valor_kusd']:,.0f} miles en 2025 a {len(destinos_2025)} destinos")
print(f"El mundo exporto rosas por USD {mundo_oferta['valor_kusd']:,.0f} miles; {len(exportadores)} paises exportadores")
destinos_2025[["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_pct", "cuota_en_socio_pct", "crec_valor_5a_pct"]].head(10)
'''),
    code('''
canasta_co_exp    = leer_canasta(ruta("canasta_co_exp"))
canasta_co_imp    = leer_canasta(ruta("canasta_co_imp"))
canasta_mundo_exp = leer_canasta(ruta("canasta_mundo_exp"))

print("Capitulo 06 (plantas vivas y flores) en la canasta exportadora colombiana, USD miles:")
print(fila_canasta(canasta_co_exp, "06").round(0).to_string())
print("\\nExportaciones mundiales totales (TOTAL), USD miles:")
print(fila_canasta(canasta_mundo_exp, "TOTAL").round(0).to_string())
'''),

    md("---\n# 2. Series por destino, 2016-2025, y CAGR"),
    code('''
paises_serie = serie[serie["codigo"] != "000"]
top4 = paises_serie[paises_serie["anio"] == 2025].nlargest(4, "valor_kusd")["pais"].tolist()

series_top = (paises_serie.assign(grupo=lambda d: np.where(d["pais"].isin(top4), d["pais"], "Otros"))
                          .groupby(["anio", "grupo"])["valor_kusd"].sum()
                          .unstack("grupo")[top4 + ["Otros"]])
exportar(series_top.reset_index(), "g7_series_destinos")
series_top
'''),
    code('''
fig, ax = plt.subplots(figsize=(10, 5))
colores = CATEGORIAS + [GRIS_MID]
for color, columna in zip(colores, series_top.columns):
    ax.plot(series_top.index, series_top[columna], color=color, linewidth=2.2, marker="o", markersize=5, label=columna)
ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
ax.set_xticks(series_top.index)
ax.legend(frameon=False, fontsize=9, loc="upper left")
estilo(ax, "Exportaciones colombianas de rosas por destino, 2016-2025",
       "HS 060311, USD (los valores del archivo vienen en miles)", "Trade Map (ITC), 2025.", eje_y="USD")
guardar(fig, "g7_series_destinos")
'''),
    code('''
# CAGR 2016-2025 y 2020-2025 por destino (los diez mayores de 2025)
ancho = paises_serie.pivot(index="pais", columns="anio", values="valor_kusd")
top10 = ancho[2025].nlargest(10).index
tabla_cagr = pd.DataFrame({
    "valor_2016": ancho.loc[top10, 2016],
    "valor_2025": ancho.loc[top10, 2025],
    "cagr_2016_2025_pct": [cagr(ancho.loc[p, 2016], ancho.loc[p, 2025], 9) for p in top10],
    "cagr_2020_2025_pct": [cagr(ancho.loc[p, 2020], ancho.loc[p, 2025], 5) for p in top10],
}).reset_index()
exportar(tabla_cagr, "g7_cagr_destinos")
tabla_cagr
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 5))
orden = tabla_cagr.sort_values("cagr_2016_2025_pct")
colores = [ROJO if v < 0 else AZUL for v in orden["cagr_2016_2025_pct"]]
ax.barh(orden["pais"], orden["cagr_2016_2025_pct"], color=colores, height=0.6)
for y, v in enumerate(orden["cagr_2016_2025_pct"]):
    ax.annotate(f"{v:+.1f} %", (v, y), textcoords="offset points", xytext=(4 if v >= 0 else -4, 0),
                ha="left" if v >= 0 else "right", va="center", fontsize=9, color=GRIS_TEXT)
ax.axvline(0, color=GRIS_EJE, linewidth=0.8)
estilo(ax, "Crecimiento anual compuesto por destino, 2016-2025",
       "Diez mayores destinos de 2025", "Trade Map (ITC), 2025.", eje_x="CAGR (%)", rejilla="x")
guardar(fig, "g7_cagr_destinos")
'''),
    analisis("¿Qué destinos crecen, cuáles se estancan, y qué cambió después de 2020?"),

    md("---\n# 3. Concentración de destinos: HHI, CR3 y número equivalente"),
    code('''
concentracion = (paises_serie.groupby("anio")["valor_kusd"]
                 .agg(HHI=hhi, CR3=lambda v: cr_n(v, 3), destinos_activos=lambda v: int((v > 0).sum()))
                 .reset_index())
concentracion["numero_equivalente"] = numeros_equivalentes(concentracion["HHI"])
exportar(concentracion, "g7_hhi_destinos")
concentracion
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.plot(concentracion["anio"], concentracion["HHI"], color=AZUL, linewidth=2.4, marker="o", markersize=7)
for _, fila in concentracion.iterrows():
    ax.annotate(f"{fila['HHI']:.3f}", (fila["anio"], fila["HHI"]), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
ax.axhspan(0.18, 1, color=ROJO, alpha=0.06)
ax.axhspan(0.15, 0.18, color=NARANJA, alpha=0.06)
ax.set_ylim(0, max(0.8, concentracion["HHI"].max() * 1.15))
ax.set_xticks(concentracion["anio"])
estilo(ax, "HHI de destinos de las rosas colombianas, 2016-2025",
       "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", "Trade Map (ITC), 2025.", eje_y="HHI")
guardar(fig, "g7_hhi_destinos")
'''),
    code('''
# Participacion por destino en 2025
participacion = destinos_2025.nlargest(12, "valor_kusd")[["pais", "valor_kusd", "participacion_pct"]]
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = participacion.sort_values("participacion_pct")
ax.barh(orden["pais"], orden["participacion_pct"], color=AZUL, height=0.6)
for y, v in enumerate(orden["participacion_pct"]):
    ax.annotate(f"{v:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Participación de cada destino en las exportaciones colombianas de rosas, 2025",
       f"HHI = {concentracion.iloc[-1]['HHI']:.3f}  |  CR3 = {concentracion.iloc[-1]['CR3']:.1f} %  |  número equivalente = {concentracion.iloc[-1]['numero_equivalente']:.1f}",
       "Trade Map (ITC), 2025.", eje_x="% del valor exportado", rejilla="x")
guardar(fig, "g7_participacion_destinos_2025")
'''),
    analisis("¿La concentración es un riesgo o una fortaleza para la Rosa Freedom? ¿Cambió la tendencia?"),

    md("---\n# 4. Balanza Comercial Relativa"),
    code('''
mundo_imp_2025, _ = separar_mundo(imp_2025)
bcr_rosas = float(ibcr(mundo_2025["valor_kusd"], mundo_imp_2025["valor_kusd"]))

# La misma medida para el capitulo 06 completo (flores y plantas), 2021-2025, con la canasta del curso
x06, m06 = fila_canasta(canasta_co_exp, "06"), fila_canasta(canasta_co_imp, "06")
bcr_serie = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA], "X_cap06": x06.values, "M_cap06": m06.values})
bcr_serie["BCR_cap06"] = ibcr(bcr_serie["X_cap06"], bcr_serie["M_cap06"])

print(f"BCR rosas (HS 060311), 2025: X = {mundo_2025['valor_kusd']:,.0f}  M = {mundo_imp_2025['valor_kusd']:,.0f}  ->  BCR = {bcr_rosas:+.4f}")
exportar(bcr_serie, "g7_bcr")
bcr_serie
'''),
    code('''
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(bcr_serie["anio"], bcr_serie["BCR_cap06"], color=VERDE, linewidth=2.2, marker="o", markersize=6, label="Capítulo 06 (flores y plantas)")
ax.scatter([2025], [bcr_rosas], color=AZUL, s=70, zorder=3, label="Rosas HS 060311, 2025")
ax.annotate(f"{bcr_rosas:+.3f}", (2025, bcr_rosas), textcoords="offset points", xytext=(8, -4), fontsize=9, color=GRIS_TEXT)
ax.set_ylim(-1.05, 1.05)
ax.axhline(0, color=GRIS_EJE, linewidth=0.8)
ax.set_xticks(bcr_serie["anio"])
ax.legend(frameon=False, fontsize=9, loc="lower left")
estilo(ax, "Balanza Comercial Relativa: rosas y capítulo 06", "+1 = exportador neto puro; -1 = importador neto puro",
       "Trade Map (ITC), 2025.", eje_y="BCR")
guardar(fig, "g7_bcr")
'''),
    analisis(),

    md("---\n# 5. Participación de mercado en cada destino\n\nLa columna `cuota_en_socio_pct` de Trade Map es exactamente la definición de la ficha: exportaciones de Colombia al destino sobre las importaciones totales de rosas de ese destino."),
    code('''
mercados = destinos_2025.nlargest(15, "valor_kusd")[
    ["pais", "valor_kusd", "cuota_en_socio_pct", "ranking_socio", "crec_valor_5a_pct", "crec_importaciones_socio_5a_pct", "valor_unitario"]]
exportar(mercados, "g7_participacion_mercado")
mercados
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = mercados.dropna(subset=["cuota_en_socio_pct"]).sort_values("cuota_en_socio_pct")
ax.barh(orden["pais"], orden["cuota_en_socio_pct"], color=AZUL, height=0.6)
for y, (v, r) in enumerate(zip(orden["cuota_en_socio_pct"], orden["ranking_socio"])):
    ax.annotate(f"{v:.1f} %  (proveedor n.º {r:.0f})", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Cuota de Colombia en las importaciones de rosas de cada destino, 2025",
       "Quince mayores destinos por valor exportado", "Trade Map (ITC), 2025.", eje_x="% de las importaciones del destino", rejilla="x")
guardar(fig, "g7_cuota_en_destino")
'''),
    code('''
# Cuota actual frente a crecimiento de la demanda del destino (importaciones totales de rosas del socio, 5 anios)
fig, ax = plt.subplots(figsize=(9, 6))
puntos = mercados.dropna(subset=["cuota_en_socio_pct", "crec_importaciones_socio_5a_pct"])
tamanos = puntos["valor_kusd"] / puntos["valor_kusd"].max() * 900 + 40
ax.scatter(puntos["cuota_en_socio_pct"], puntos["crec_importaciones_socio_5a_pct"], s=tamanos, color=AZUL, alpha=0.55, edgecolor="white", linewidth=1.5)
for _, p in puntos.iterrows():
    ax.annotate(p["pais"], (p["cuota_en_socio_pct"], p["crec_importaciones_socio_5a_pct"]),
                textcoords="offset points", xytext=(6, 4), fontsize=8.5, color=GRIS_TEXT)
ax.axhline(puntos["crec_importaciones_socio_5a_pct"].median(), color=GRIS_EJE, linewidth=0.8, linestyle="--")
ax.axvline(puntos["cuota_en_socio_pct"].median(), color=GRIS_EJE, linewidth=0.8, linestyle="--")
estilo(ax, "Cuota de Colombia frente al crecimiento de las importaciones de cada destino",
       "Tamaño del punto = valor exportado en 2025. Líneas punteadas = medianas", "Trade Map (ITC), 2025.",
       eje_x="Cuota de Colombia en el destino (%)", eje_y="Crecimiento de las importaciones del destino, 5 años (%)")
guardar(fig, "g7_cuota_vs_crecimiento")
'''),
    analisis("¿En qué cuadrante cae cada mercado candidato (Estados Unidos, Canadá, Reino Unido, Países Bajos, Japón)?"),

    md("---\n# 6. Valor unitario\n\nComo advierte la ficha, el valor unitario **no equivale a margen ni a precio neto**: es valor FOB dividido por toneladas."),
    code('''
# Colombia frente a los grandes exportadores (se excluyen los que no reportan cantidad)
competidores = exportadores.nlargest(10, "valor_kusd")
competidores = competidores[(competidores["cantidad"] > 0) & competidores["valor_unitario"].notna()]
competidores = competidores[["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_mundial_pct"]]
exportar(competidores, "g7_valor_unitario_competidores")
competidores
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 5))
orden = competidores.sort_values("valor_unitario")
colores = [NARANJA if p == "Colombia" else GRIS_MID for p in orden["pais"]]
ax.barh(orden["pais"], orden["valor_unitario"], color=colores, height=0.6)
for y, v in enumerate(orden["valor_unitario"]):
    ax.annotate(f"{v:,.0f}", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Valor unitario de las exportaciones de rosas: Colombia frente a los grandes exportadores, 2025",
       "USD por tonelada, valor FOB / cantidad", "Trade Map (ITC), 2025.", eje_x="USD/t", rejilla="x")
guardar(fig, "g7_valor_unitario_competidores")
'''),
    code('''
# Valor unitario por destino de Colombia
vu_destinos = destinos_2025.nlargest(12, "valor_kusd")
vu_destinos = vu_destinos[vu_destinos["cantidad"] > 0][["pais", "valor_kusd", "cantidad", "valor_unitario"]]
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = vu_destinos.sort_values("valor_unitario")
ax.barh(orden["pais"], orden["valor_unitario"], color=AZUL, height=0.6)
ax.axvline(mundo_2025["valor_unitario"], color=NARANJA, linewidth=1.5, linestyle="--")
ax.annotate(f"promedio Colombia {mundo_2025['valor_unitario']:,.0f}", (mundo_2025["valor_unitario"], len(orden) - 0.4),
            fontsize=9, color=NARANJA, ha="left", xytext=(4, 0), textcoords="offset points")
for y, v in enumerate(orden["valor_unitario"]):
    ax.annotate(f"{v:,.0f}", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Valor unitario de las rosas colombianas por destino, 2025", "USD por tonelada",
       "Trade Map (ITC), 2025.", eje_x="USD/t", rejilla="x")
guardar(fig, "g7_valor_unitario_destinos")
exportar(vu_destinos, "g7_valor_unitario_destinos")
'''),
    analisis(),

    md("---\n# 7. Cuota en la oferta mundial"),
    code('''
oferta = exportadores.nlargest(10, "valor_kusd")[["pais", "valor_kusd", "participacion_mundial_pct", "crec_valor_5a_pct"]]
hhi_oferta = hhi(exportadores["valor_kusd"])
print(f"HHI de la oferta mundial de rosas, 2025: {hhi_oferta:.4f}  (número equivalente de exportadores: {numeros_equivalentes(hhi_oferta):.1f})")
fig, ax = plt.subplots(figsize=(9, 5))
orden = oferta.sort_values("participacion_mundial_pct")
colores = [NARANJA if p == "Colombia" else GRIS_MID for p in orden["pais"]]
ax.barh(orden["pais"], orden["participacion_mundial_pct"], color=colores, height=0.6)
for y, v in enumerate(orden["participacion_mundial_pct"]):
    ax.annotate(f"{v:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Diez mayores exportadores de rosas del mundo, 2025", "Participación en el valor exportado mundial",
       "Trade Map (ITC), 2025.", eje_x="% del valor mundial", rejilla="x")
guardar(fig, "g7_oferta_mundial")
exportar(oferta, "g7_oferta_mundial")
'''),
    analisis(),

    md("---\n# 8. Ventaja comparativa revelada: RCA de Balassa, RSCA y NRCA\n\nEl numerador sale de las descargas del equipo; el denominador mundial (exportaciones totales de todos los productos) sale de la canasta del curso `mundo_exp_productos_hs2_serie.csv`, fila TOTAL."),
    code('''
X_ij = mundo_2025["valor_kusd"]                                   # Colombia exporta rosas, 2025
X_i  = separar_mundo(exp_all)[0]["valor_kusd"]                    # Colombia exporta todo, 2025
X_j  = mundo_oferta["valor_kusd"]                                  # el mundo exporta rosas, 2025
X_w  = fila_canasta(canasta_mundo_exp, "TOTAL")["2025"]            # el mundo exporta todo, 2025

vcr = pd.DataFrame({
    "indice": ["RCA (Balassa)", "RSCA (Laursen)", "NRCA (Yu, Cai y Leung) x 10^4"],
    "valor": [float(rca_balassa(X_ij, X_i, X_j, X_w)),
              float(rsca_laursen(rca_balassa(X_ij, X_i, X_j, X_w))),
              float(nrca(X_ij, X_i, X_j, X_w)) * 1e4],
    "umbral_neutral": [1, 0, 0],
})
print(f"X_ij = {X_ij:,.0f}   X_i = {X_i:,.0f}   X_j = {X_j:,.0f}   X_w = {X_w:,.0f}   (USD miles)")
exportar(vcr, "g7_vcr_2025")
vcr
'''),
    code('''
# La misma familia para el capitulo 06 completo, 2021-2025, con la canasta del curso
vcr_serie = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA]})
vcr_serie["RCA_cap06"] = rca_balassa(fila_canasta(canasta_co_exp, "06"), fila_canasta(canasta_co_exp, "TOTAL"),
                                     fila_canasta(canasta_mundo_exp, "06"), fila_canasta(canasta_mundo_exp, "TOTAL"))
vcr_serie["RSCA_cap06"] = rsca_laursen(vcr_serie["RCA_cap06"])
exportar(vcr_serie, "g7_vcr_serie_cap06")

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(vcr_serie["anio"], vcr_serie["RSCA_cap06"], color=VERDE, linewidth=2.2, marker="o", markersize=6, label="Capítulo 06, RSCA")
ax.scatter([2025], [vcr.loc[1, "valor"]], color=AZUL, s=70, zorder=3, label="Rosas HS 060311, RSCA 2025")
for _, fila in vcr_serie.iterrows():
    ax.annotate(f"{fila['RSCA_cap06']:.2f}", (fila["anio"], fila["RSCA_cap06"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
ax.set_ylim(-1.05, 1.05)
ax.axhline(0, color=GRIS_EJE, linewidth=0.8)
ax.set_xticks(vcr_serie["anio"])
ax.legend(frameon=False, fontsize=9, loc="lower left")
estilo(ax, "Ventaja comparativa revelada simétrica (RSCA)", "0 = neutral; +1 = especialización máxima",
       "Trade Map (ITC), 2025; canasta HS2 del curso.", eje_y="RSCA")
guardar(fig, "g7_rsca")
vcr_serie
'''),
    analisis("¿La ventaja es de las rosas en particular o del sector floricultor completo?"),

    md("---\n# 9. Índice de Lafay"),
    code('''
# (a) Las rosas dentro del comercio total de Colombia, 2025
M_ij = mundo_imp_2025["valor_kusd"]
M_i  = separar_mundo(imp_all)[0]["valor_kusd"]
ibcr_rosas = (X_ij - M_ij) / (X_ij + M_ij)
ibcr_pais  = (X_i - M_i) / (X_i + M_i)
peso_rosas = (X_ij + M_ij) / (X_i + M_i)
lfi_rosas  = 100 * (ibcr_rosas - ibcr_pais) * peso_rosas
print(f"Lafay rosas 2025: IBCR producto = {ibcr_rosas:+.4f} | IBCR pais = {ibcr_pais:+.4f} | peso = {peso_rosas:.4%} | LFI = {lfi_rosas:+.4f}")

# (b) Lafay de los 97 capitulos de la canasta, 2025, para ubicar el capitulo 06 en contexto
capitulos = canasta_co_exp[canasta_co_exp["codigo"] != "TOTAL"][["codigo", "producto", "2025"]].rename(columns={"2025": "X"})
capitulos = capitulos.merge(canasta_co_imp[["codigo", "2025"]].rename(columns={"2025": "M"}), on="codigo", how="inner")
capitulos["LFI"] = lafay(capitulos["X"], capitulos["M"])
capitulos["producto"] = capitulos["producto"].str.slice(0, 45)
ranking_lafay = capitulos.sort_values("LFI", ascending=False).reset_index(drop=True)
exportar(ranking_lafay, "g7_lafay_capitulos")
ranking_lafay.head(10)
'''),
    code('''
extremos = pd.concat([ranking_lafay.head(8), ranking_lafay.tail(5)]).sort_values("LFI")
fig, ax = plt.subplots(figsize=(9, 6))
colores = [NARANJA if c == "06" else (AZUL if v >= 0 else ROJO) for c, v in zip(extremos["codigo"], extremos["LFI"])]
ax.barh(extremos["codigo"] + "  " + extremos["producto"], extremos["LFI"], color=colores, height=0.6)
ax.axvline(0, color=GRIS_EJE, linewidth=0.8)
estilo(ax, "Índice de Lafay por capítulo HS2, Colombia 2025", "Ocho mayores y cinco menores; el capítulo 06 resaltado",
       "Trade Map (ITC), canasta HS2 del curso.", eje_x="LFI", rejilla="x")
guardar(fig, "g7_lafay_capitulos")
'''),
    analisis(),

    md("---\n# 10. Matriz de decisión 0-100 y prueba de sensibilidad\n\nLa ficha define cuatro dimensiones con pesos 35 / 25 / 20 / 20 y un semáforo **A Crecer / B Defender / C Pilotear / D Monitorear**. Los puntajes de cada mercado (0 a 100) son **juicio del equipo**, apoyado en las tablas anteriores. La tabla siguiente reúne los datos disponibles para cada candidato; después viene la celda editable."),
    code('''
CANDIDATOS = ["Estados Unidos de América", "Canadá", "Reino Unido", "Países Bajos", "Japón"]
datos_candidatos = mercados[mercados["pais"].isin(CANDIDATOS)].set_index("pais").reindex(CANDIDATOS)
datos_candidatos = datos_candidatos.join(tabla_cagr.set_index("pais")[["cagr_2016_2025_pct"]])
exportar(datos_candidatos.reset_index(), "g7_datos_candidatos")
datos_candidatos
'''),
    code('''
# ====================== EDITABLE: pesos y puntajes 0-100 ======================
PESOS = {                                     # los de la ficha; se normalizan solos
    "Competitividad revelada": 35,
    "Atractivo de mercado":    25,
    "Economía de la operación": 20,
    "Acceso y riesgo":          20,
}
PUNTAJES = pd.DataFrame({                     # filas = dimensiones, columnas = mercados; 0 a 100
    "Estados Unidos de América": [50, 50, 50, 50],
    "Canadá":                    [50, 50, 50, 50],
    "Reino Unido":               [50, 50, 50, 50],
    "Países Bajos":              [50, 50, 50, 50],
    "Japón":                     [50, 50, 50, 50],
}, index=list(PESOS.keys()))
UMBRALES = {"A Crecer": 75, "B Defender": 60, "C Pilotear": 45}   # por debajo del ultimo: D Monitorear
# ==============================================================================

def semaforo(total):
    for etiqueta, umbral in UMBRALES.items():
        if total >= umbral:
            return etiqueta
    return "D Monitorear"

matriz = matriz_multicriterio(PUNTAJES, PESOS)
matriz["Semáforo"] = matriz["Total"].apply(semaforo)
exportar(matriz.reset_index().rename(columns={"index": "mercado"}), "g7_matriz_decision")
matriz
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 4.8))
acumulado = np.zeros(len(matriz))
for color, dimension in zip(CATEGORIAS, PESOS.keys()):
    ax.barh(matriz.index, matriz[dimension], left=acumulado, color=color, height=0.6, label=dimension, edgecolor="white", linewidth=1.5)
    acumulado += matriz[dimension].values
for y, (t, s) in enumerate(zip(matriz["Total"], matriz["Semáforo"])):
    ax.annotate(f"{t:.0f}  {s}", (t, y), textcoords="offset points", xytext=(5, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.invert_yaxis()
ax.set_xlim(0, 115)
leyenda_fuera(ax)
estilo(ax, "Puntaje ponderado por mercado (0-100)", "Contribución de cada dimensión según los pesos de la ficha",
       "Elaboración del equipo.", eje_x="Puntaje", rejilla="x")
guardar(fig, "g7_matriz_decision")
'''),
    code('''
# Prueba de sensibilidad: se mueve cada peso +/- 5 puntos (redistribuyendo el resto) y se mira si cambia el orden
def sensibilidad(puntajes, pesos, delta=5):
    base = matriz_multicriterio(puntajes, pesos).index.tolist()
    filas = []
    for dimension in pesos:
        for signo in (+delta, -delta):
            alterados = dict(pesos)
            alterados[dimension] = max(0, alterados[dimension] + signo)
            orden = matriz_multicriterio(puntajes, alterados).index.tolist()
            filas.append({"peso_modificado": dimension, "cambio": f"{signo:+d}",
                          "primero": orden[0], "orden_completo": " > ".join(orden),
                          "cambia_el_lider": orden[0] != base[0], "cambia_el_orden": orden != base})
    return pd.DataFrame(filas)

prueba = sensibilidad(PUNTAJES, PESOS)
print("Orden base:", " > ".join(matriz.index))
print(f"El líder cambia en {prueba['cambia_el_lider'].sum()} de {len(prueba)} escenarios; el orden completo cambia en {prueba['cambia_el_orden'].sum()}.")
exportar(prueba, "g7_sensibilidad")
prueba
'''),
    analisis("Según la regla de la ficha: si una pequeña modificación cambia el ranking, la conclusión es de confianza media. ¿Qué confianza tiene la suya?"),

    cierre([REF_BALASSA, REF_YU, REF_LAFAY, REF_BAENA]),
]

escribir(celdas, NB)
