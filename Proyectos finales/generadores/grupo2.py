from comun import *

G = "Proyectos finales/Grupo 2"
D = G + "/datos/"
NB = G + "/Grupo_2_Cacao.ipynb"

ARCHIVOS = {
    "exp_serie": D + "colombias-exports-to-world-by-importer_1801.csv",
    "exp_2025":  D + "colombias-exports-to-world-in-2025-by-importer_1801.csv",
    "imp_2025":  D + "colombias-imports-from-world-in-2025-by-exporter_1801.csv",
    "mundo_exp": D + "exporting-countries-in-2025_1801.csv",
    "mundo_imp": D + "importing-countries-in-2025_1801.csv",
    "faostat":   D + "faostat_cacao_2015_2024.csv",
    "canasta_co_exp":    "data/co_exp_productos_hs2_serie.xls",
    "canasta_mundo_exp": "data/mundo_exp_productos_hs2_serie.csv",
}

METR = [
    ("Evolución y participación por destino", "¿A quién le vende Colombia su cacao y cómo ha cambiado desde 2016?"),
    ("Concentración de destinos (HHI, CR3)", "¿De cuántos compradores depende el cacao colombiano?"),
    ("RCA de Balassa y RSCA", "¿Colombia está especializada en cacao frente al resto del mundo?"),
    ("Participación de mercado en cada país candidato", "¿Qué porción de las importaciones de cacao de cada mercado es colombiana?"),
    ("Competidores en la oferta mundial", "¿Cómo se compara Colombia con Ecuador, Perú, Ghana y Côte d'Ivoire?"),
    ("Tamaño y crecimiento de los mercados importadores", "¿Dónde está la demanda y dónde crece?"),
    ("Producción, área y rendimiento (FAOSTAT)", "¿Qué tan competitiva es la base productiva colombiana?"),
    ("Matriz de decisión ponderada", "¿Qué mercado destino es el más atractivo con seis variables y pesos explícitos?"),
    ("Indicadores de impacto social", "¿Qué evidencia cuantitativa respalda al cacao como alternativa a los cultivos ilícitos?"),
]

celdas = [
    badge(NB),
    portada("Grupo 2. El negocio que puede ganarle a la coca: el potencial exportador del cacao colombiano",
            "Grupo 2", "Cacao en grano, **HS 1801**",
            "¿Cómo aprovechar el potencial exportador del cacao fino de aroma colombiano como alternativa económica frente a los cultivos ilícitos?",
            METR, "*Equipo 2 — Ficha técnica del estudio* (septiembre de 2026). Los datos de Trade Map y FAOSTAT que la ficha describe se descargaron para este cuaderno y están en la carpeta `datos/` del grupo."),
    md("---\n# 0. Preparación del entorno"),
    CELL_IMPORTS,
    cell_config(G, ARCHIVOS),
    CELL_DESCARGA,
    CELL_LECTORES,
    cell_metricas(["hhi", "cr", "ibcr", "rca", "cagr", "multicriterio"]),

    md("---\n# 1. Los datos\n\nCinco tablas de Trade Map (HS 1801), la serie de FAOSTAT para cinco países productores y dos archivos de la canasta HS2 del curso, que aportan las exportaciones totales de Colombia y del mundo para el denominador del RCA."),
    code('''
serie     = leer_serie_trademap(ruta("exp_serie"))     # Colombia exporta cacao por destino, 2016-2025
exp_2025  = leer_trademap(ruta("exp_2025"))            # lo mismo, corte 2025 con indicadores
imp_2025  = leer_trademap(ruta("imp_2025"))            # Colombia importa cacao por origen, 2025
mundo_exp = leer_trademap(ruta("mundo_exp"))           # exportadores mundiales de cacao, 2025
mundo_imp = leer_trademap(ruta("mundo_imp"))           # importadores mundiales de cacao, 2025
faostat   = pd.read_csv(ruta("faostat"), encoding="utf-8")

mundo_2025, destinos_2025 = separar_mundo(exp_2025)
mundo_oferta, exportadores = separar_mundo(mundo_exp)
mundo_demanda, importadores = separar_mundo(mundo_imp)
canasta_co_exp    = leer_canasta(ruta("canasta_co_exp"))
canasta_mundo_exp = leer_canasta(ruta("canasta_mundo_exp"))

print(f"Colombia exporto cacao por USD {mundo_2025['valor_kusd']:,.0f} miles en 2025 a {len(destinos_2025)} destinos")
print(f"El mundo exporto cacao por USD {mundo_oferta['valor_kusd']:,.0f} miles ({len(exportadores)} exportadores, {len(importadores)} importadores)")
destinos_2025[["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_pct", "cuota_en_socio_pct", "crec_valor_5a_pct"]].head(10)
'''),
    code('''
anios_fao = [c for c in faostat.columns if c.startswith("Y")]
fao_largo = faostat.melt(id_vars=["Area", "Element", "Unit"], value_vars=anios_fao, var_name="anio", value_name="valor")
fao_largo["anio"] = fao_largo["anio"].str[1:].astype(int)
fao_largo["Area"] = fao_largo["Area"].replace({"Peru": "Perú"})
fao_largo.pivot_table(index="Area", columns="Element", values="valor", aggfunc="last")   # ultimo anio disponible
'''),

    md("---\n# 2. Evolución y participación por destino, 2016-2025"),
    code('''
paises_serie = serie[serie["codigo"] != "000"]
top4 = paises_serie[paises_serie["anio"] == 2025].nlargest(4, "valor_kusd")["pais"].tolist()
series_top = (paises_serie.assign(grupo=lambda d: np.where(d["pais"].isin(top4), d["pais"], "Otros"))
                          .groupby(["anio", "grupo"])["valor_kusd"].sum().unstack("grupo")[top4 + ["Otros"]])
participacion_serie = series_top.div(series_top.sum(axis=1), axis=0) * 100
exportar(series_top.reset_index(), "g2_series_destinos")
series_top
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colores = CATEGORIAS + [GRIS_MID]
for color, columna in zip(colores, series_top.columns):
    axes[0].plot(series_top.index, series_top[columna], color=color, linewidth=2.2, marker="o", markersize=5, label=columna)
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
axes[0].set_xticks(series_top.index)
axes[0].legend(frameon=False, fontsize=9, loc="upper left")
estilo(axes[0], "Valor exportado por destino", "USD, cuatro mayores destinos de 2025 y el resto", eje_y="USD")

axes[1].stackplot(participacion_serie.index, [participacion_serie[c] for c in participacion_serie.columns],
                  colors=colores, labels=participacion_serie.columns, alpha=0.9)
axes[1].set_ylim(0, 100)
axes[1].set_xticks(participacion_serie.index)
estilo(axes[1], "Participación de cada destino", "% del valor exportado cada año", "Trade Map (ITC), 2025.", eje_y="%")
plt.tight_layout()
guardar(fig, "g2_series_destinos")
'''),
    code('''
participacion = destinos_2025.nlargest(12, "valor_kusd")[["pais", "valor_kusd", "participacion_pct", "crec_valor_5a_pct"]]
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = participacion.sort_values("participacion_pct")
ax.barh(orden["pais"], orden["participacion_pct"], color=AZUL, height=0.6)
for y, v in enumerate(orden["participacion_pct"]):
    ax.annotate(f"{v:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Participación de cada destino en las exportaciones colombianas de cacao, 2025", "Doce mayores destinos",
       "Trade Map (ITC), 2025.", eje_x="% del valor exportado", rejilla="x")
guardar(fig, "g2_participacion_2025")
exportar(participacion, "g2_participacion_2025")
'''),
    analisis("¿Qué destinos ganaron y perdieron peso? ¿Qué pasó en 2024-2025?"),

    md("---\n# 3. Concentración de destinos: HHI, CR3 y número equivalente"),
    code('''
concentracion = (paises_serie.groupby("anio")["valor_kusd"]
                 .agg(HHI=hhi, CR3=lambda v: cr_n(v, 3), destinos_activos=lambda v: int((v > 0).sum()))
                 .reset_index())
concentracion["numero_equivalente"] = numeros_equivalentes(concentracion["HHI"])
exportar(concentracion, "g2_concentracion")
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
estilo(axes[0], "HHI de destinos del cacao colombiano", "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", eje_y="HHI")

axes[1].plot(concentracion["anio"], concentracion["CR3"], color=VERDE, linewidth=2.4, marker="o", markersize=7)
for _, fila in concentracion.iterrows():
    axes[1].annotate(f"{fila['CR3']:.0f} %", (fila["anio"], fila["CR3"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].set_ylim(0, 105)
axes[1].set_xticks(concentracion["anio"])
estilo(axes[1], "CR3: peso de los tres mayores destinos", "% del valor exportado", "Trade Map (ITC), 2025.", eje_y="%")
plt.tight_layout()
guardar(fig, "g2_concentracion")
'''),
    analisis(),

    md("---\n# 4. Ventaja comparativa revelada: RCA de Balassa y RSCA\n\nNumerador: exportaciones de cacao de Colombia y del mundo (Trade Map). Denominador: exportaciones totales de Colombia y del mundo, fila TOTAL de la canasta HS2 del curso."),
    code('''
X_ij = mundo_2025["valor_kusd"]                                    # Colombia exporta cacao, 2025
X_i  = fila_canasta(canasta_co_exp, "TOTAL")["2025"]               # Colombia exporta todo, 2025
X_j  = mundo_oferta["valor_kusd"]                                   # el mundo exporta cacao, 2025
X_w  = fila_canasta(canasta_mundo_exp, "TOTAL")["2025"]            # el mundo exporta todo, 2025
rca_1801 = float(rca_balassa(X_ij, X_i, X_j, X_w))
print(f"X_ij = {X_ij:,.0f}   X_i = {X_i:,.0f}   X_j = {X_j:,.0f}   X_w = {X_w:,.0f}  (USD miles)")
print(f"RCA cacao en grano (HS 1801), 2025 = {rca_1801:.3f}   |   RSCA = {float(rsca_laursen(rca_1801)):+.3f}")

# Serie 2021-2025 para el capitulo 18 completo (cacao y sus preparaciones)
vcr_serie = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA]})
vcr_serie["RCA_cap18"] = rca_balassa(fila_canasta(canasta_co_exp, "18"), fila_canasta(canasta_co_exp, "TOTAL"),
                                     fila_canasta(canasta_mundo_exp, "18"), fila_canasta(canasta_mundo_exp, "TOTAL"))
vcr_serie["RSCA_cap18"] = rsca_laursen(vcr_serie["RCA_cap18"])
exportar(vcr_serie, "g2_rca_serie")
vcr_serie
'''),
    code('''
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(vcr_serie["anio"], vcr_serie["RCA_cap18"], color=VERDE, linewidth=2.2, marker="o", markersize=6, label="Capítulo 18 (cacao y preparaciones)")
ax.scatter([2025], [rca_1801], color=AZUL, s=70, zorder=3, label="Cacao en grano HS 1801, 2025")
for _, fila in vcr_serie.iterrows():
    ax.annotate(f"{fila['RCA_cap18']:.2f}", (fila["anio"], fila["RCA_cap18"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
ax.annotate(f"{rca_1801:.2f}", (2025, rca_1801), textcoords="offset points", xytext=(8, -4), fontsize=9, color=GRIS_TEXT)
ax.axhline(1, color=GRIS_EJE, linewidth=0.8, linestyle="--")
ax.set_xticks(vcr_serie["anio"])
ax.set_ylim(0, max(2, vcr_serie["RCA_cap18"].max(), rca_1801) * 1.2)
ax.legend(frameon=False, fontsize=9, loc="upper left")
estilo(ax, "RCA de Balassa: cacao colombiano", "Línea punteada = 1 (umbral de especialización revelada)",
       "Trade Map (ITC), 2025; canasta HS2 del curso.", eje_y="RCA")
guardar(fig, "g2_rca")
'''),
    analisis(),

    md("---\n# 5. Participación de Colombia en las importaciones de cada mercado\n\n`cuota_en_socio_pct` = exportaciones de Colombia al país / importaciones totales de cacao de ese país."),
    code('''
mercados = destinos_2025.nlargest(15, "valor_kusd")[
    ["pais", "valor_kusd", "cuota_en_socio_pct", "ranking_socio", "crec_valor_5a_pct", "crec_importaciones_socio_5a_pct", "valor_unitario"]]
exportar(mercados, "g2_cuota_mercados")
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = mercados.dropna(subset=["cuota_en_socio_pct"]).sort_values("cuota_en_socio_pct")
ax.barh(orden["pais"], orden["cuota_en_socio_pct"], color=AZUL, height=0.6)
for y, (v, r) in enumerate(zip(orden["cuota_en_socio_pct"], orden["ranking_socio"])):
    ax.annotate(f"{v:.2f} %  (proveedor n.º {r:.0f})", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Cuota de Colombia en las importaciones de cacao de cada destino, 2025", "Quince mayores destinos por valor",
       "Trade Map (ITC), 2025.", eje_x="% de las importaciones del destino", rejilla="x")
guardar(fig, "g2_cuota_mercados")
mercados
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 6))
puntos = mercados.dropna(subset=["cuota_en_socio_pct", "crec_importaciones_socio_5a_pct"])
tamanos = puntos["valor_kusd"] / puntos["valor_kusd"].max() * 900 + 40
ax.scatter(puntos["cuota_en_socio_pct"], puntos["crec_importaciones_socio_5a_pct"], s=tamanos, color=AZUL, alpha=0.55, edgecolor="white", linewidth=1.5)
for _, p in puntos.iterrows():
    ax.annotate(p["pais"], (p["cuota_en_socio_pct"], p["crec_importaciones_socio_5a_pct"]), textcoords="offset points", xytext=(6, 4), fontsize=8.5, color=GRIS_TEXT)
ax.axhline(puntos["crec_importaciones_socio_5a_pct"].median(), color=GRIS_EJE, linewidth=0.8, linestyle="--")
ax.axvline(puntos["cuota_en_socio_pct"].median(), color=GRIS_EJE, linewidth=0.8, linestyle="--")
estilo(ax, "Cuota de Colombia frente al crecimiento de las importaciones de cada destino",
       "Tamaño del punto = valor exportado por Colombia en 2025. Líneas punteadas = medianas", "Trade Map (ITC), 2025.",
       eje_x="Cuota de Colombia en el destino (%)", eje_y="Crecimiento de las importaciones del destino, 5 años (%)")
guardar(fig, "g2_cuota_vs_crecimiento")
'''),
    analisis(),

    md("---\n# 6. Competidores en la oferta mundial"),
    code('''
COMPETIDORES = ["Colombia", "Ecuador", "Perú", "Ghana", "Côte d'Ivoire"]
oferta = exportadores.nlargest(10, "valor_kusd")[["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_mundial_pct", "crec_valor_5a_pct"]]
oferta = pd.concat([oferta, exportadores[exportadores["pais"].isin(COMPETIDORES) & ~exportadores["pais"].isin(oferta["pais"])]
                    [oferta.columns]]).drop_duplicates("pais")
hhi_oferta = hhi(exportadores["valor_kusd"])
print(f"HHI de la oferta mundial de cacao 2025: {hhi_oferta:.4f}  (número equivalente: {numeros_equivalentes(hhi_oferta):.1f} exportadores)")
exportar(oferta, "g2_oferta_mundial")
oferta
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
orden = oferta.sort_values("participacion_mundial_pct")
colores = [NARANJA if p == "Colombia" else (AZUL if p in COMPETIDORES else GRIS_MID) for p in orden["pais"]]
axes[0].barh(orden["pais"], orden["participacion_mundial_pct"], color=colores, height=0.6)
for y, v in enumerate(orden["participacion_mundial_pct"]):
    axes[0].annotate(f"{v:.2f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(axes[0], "Cuota en el valor exportado mundial", "Diez mayores exportadores más los competidores de la ficha", eje_x="%", rejilla="x")

vu = orden[orden["cantidad"] > 0].sort_values("valor_unitario")
colores = [NARANJA if p == "Colombia" else (AZUL if p in COMPETIDORES else GRIS_MID) for p in vu["pais"]]
axes[1].barh(vu["pais"], vu["valor_unitario"], color=colores, height=0.6)
for y, v in enumerate(vu["valor_unitario"]):
    axes[1].annotate(f"{v:,.0f}", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(axes[1], "Valor unitario de exportación", "USD por tonelada (valor FOB / cantidad)", "Trade Map (ITC), 2025.", eje_x="USD/t", rejilla="x")
plt.tight_layout()
guardar(fig, "g2_competidores")
'''),
    analisis("Naranja = Colombia; azul = los competidores nombrados en la ficha; gris = otros grandes exportadores."),

    md("---\n# 7. Tamaño y crecimiento de los mercados importadores"),
    code('''
demanda = importadores.nlargest(12, "valor_kusd")[["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_mundial_pct", "crec_valor_5a_pct", "crec_valor_2a_pct"]]
# cuota que Colombia ya tiene en cada uno de esos mercados
demanda = demanda.merge(destinos_2025[["pais", "cuota_en_socio_pct", "ranking_socio"]], on="pais", how="left")
exportar(demanda, "g2_mercados_importadores")
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = demanda.sort_values("valor_kusd")
ax.barh(orden["pais"], orden["valor_kusd"], color=AZUL, height=0.6)
for y, (v, g) in enumerate(zip(orden["valor_kusd"], orden["crec_valor_5a_pct"])):
    ax.annotate(f"{fmt_miles(v)}   crec. 5 años {g:+.0f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.xaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
estilo(ax, "Doce mayores importadores de cacao en grano del mundo, 2025", "Valor importado (USD) y crecimiento a cinco años",
       "Trade Map (ITC), 2025.", eje_x="USD", rejilla="x")
guardar(fig, "g2_mercados_importadores")
demanda
'''),
    analisis(),

    md("---\n# 8. Base productiva: producción, área y rendimiento (FAOSTAT, 2015-2024)"),
    code('''
def panel_fao(elemento):
    return fao_largo[fao_largo["Element"] == elemento].pivot(index="anio", columns="Area", values="valor")

produccion  = panel_fao("Production")
rendimiento = panel_fao("Yield")
area        = panel_fao("Area harvested")
resumen_fao = pd.DataFrame({
    "produccion_2024_t": produccion.loc[2024],
    "area_2024_ha": area.loc[2024],
    "rendimiento_2024_kg_ha": rendimiento.loc[2024],
    "cagr_produccion_2015_2024_pct": [cagr(produccion.loc[2015, p], produccion.loc[2024, p], 9) for p in produccion.columns],
}).sort_values("produccion_2024_t", ascending=False)
exportar(resumen_fao.reset_index(), "g2_faostat_resumen")
resumen_fao
'''),
    code('''
ORDEN_PAISES = ["Colombia", "Ecuador", "Perú", "Ghana", "Côte d'Ivoire"]
colores = dict(zip(ORDEN_PAISES, [NARANJA, AZUL, VERDE, ROJO, GRIS_MID]))
fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
for ax, (tabla, titulo, unidad) in zip(axes, [(produccion, "Producción", "toneladas"), (area, "Área cosechada", "hectáreas"), (rendimiento, "Rendimiento", "kg por hectárea")]):
    for pais in ORDEN_PAISES:
        if pais in tabla.columns:
            ax.plot(tabla.index, tabla[pais], color=colores[pais], linewidth=2.2, marker="o", markersize=4, label=pais)
    ax.set_xticks(tabla.index[::3])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_unidades))
    estilo(ax, titulo, unidad, eje_y=unidad)
axes[0].legend(frameon=False, fontsize=9)
axes[2].figure.text(0.01, -0.03, "Fuente: FAOSTAT (FAO, 2025), cacao en grano, código 661.", fontsize=8, color=GRIS_EJE)
plt.tight_layout()
guardar(fig, "g2_faostat_series")
'''),
    analisis("El rendimiento por hectárea y la producción cuentan historias distintas. ¿Qué dice cada una sobre la competitividad colombiana?"),

    md("---\n# 9. Matriz de decisión ponderada\n\nLa ficha exige **mínimo seis variables cuantitativas sobre al menos cuatro mercados**. Cuatro variables salen de los datos de Trade Map (tamaño del mercado, crecimiento, precio de importación y cuota actual de Colombia); dos son **editables** porque requieren Market Access Map: arancel y barreras no arancelarias. Los pesos también son editables. Cada variable se lleva a una escala 0-100 (100 = mejor) según su dirección."),
    code('''
# ====================== EDITABLE: candidatos, pesos y variables manuales ======================
CANDIDATOS = importadores.nlargest(4, "valor_kusd")["pais"].tolist()   # cambia la lista si quieres otros mercados
PESOS = {
    "Tamaño del mercado (USD importados)": 25,
    "Crecimiento de importaciones 5 años (%)": 15,
    "Precio de importación (USD/t)": 15,
    "Cuota actual de Colombia (%)": 15,
    "Arancel aplicado a Colombia (%)": 15,       # manual: menor es mejor
    "Barreras no arancelarias (1-5)": 15,        # manual: menor es mejor
}
MANUAL = pd.DataFrame({                          # rellenar con Market Access Map / Legiscomex
    "Arancel aplicado a Colombia (%)": [0, 0, 0, 0],
    "Barreras no arancelarias (1-5)": [3, 3, 3, 3],
}, index=CANDIDATOS).T
# ==============================================================================================

base = importadores.set_index("pais").reindex(CANDIDATOS)
cuota = destinos_2025.set_index("pais")["cuota_en_socio_pct"].reindex(CANDIDATOS).fillna(0)
VARIABLES = pd.DataFrame({
    "Tamaño del mercado (USD importados)": base["valor_kusd"],
    "Crecimiento de importaciones 5 años (%)": base["crec_valor_5a_pct"],
    "Precio de importación (USD/t)": base["valor_unitario"],
    "Cuota actual de Colombia (%)": cuota,
}).T
VARIABLES = pd.concat([VARIABLES, MANUAL])
DIRECCION = {v: +1 for v in VARIABLES.index}
DIRECCION["Arancel aplicado a Colombia (%)"] = -1
DIRECCION["Barreras no arancelarias (1-5)"] = -1

def a_escala_100(fila, direccion):
    """Min-max a 0-100 en la direccion indicada (+1: mayor es mejor; -1: menor es mejor). Si todos son iguales, 50."""
    if fila.max() == fila.min():
        return pd.Series(50.0, index=fila.index)
    escala = (fila - fila.min()) / (fila.max() - fila.min()) * 100
    return escala if direccion > 0 else 100 - escala

PUNTAJES = pd.DataFrame({v: a_escala_100(VARIABLES.loc[v].astype(float), DIRECCION[v]) for v in VARIABLES.index}).T
matriz = matriz_multicriterio(PUNTAJES, PESOS)
print("Variables crudas:"); display(VARIABLES)
exportar(matriz.reset_index().rename(columns={"index": "mercado"}), "g2_matriz_decision")
matriz
'''),
    code('''
fig, ax = plt.subplots(figsize=(10, 4.8))
acumulado = np.zeros(len(matriz))
paleta = CATEGORIAS + ["#7f7d76", GRIS_MID]
for color, variable in zip(paleta, PESOS.keys()):
    ax.barh(matriz.index, matriz[variable], left=acumulado, color=color, height=0.6, label=variable, edgecolor="white", linewidth=1.5)
    acumulado += matriz[variable].values
for y, t in enumerate(matriz["Total"]):
    ax.annotate(f"{t:.0f}", (t, y), textcoords="offset points", xytext=(5, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.invert_yaxis()
ax.set_xlim(0, 110)
leyenda_fuera(ax)
estilo(ax, "Puntaje ponderado por mercado candidato (0-100)", "Contribución de cada variable según los pesos", "Trade Map (ITC) y elaboración del equipo.", eje_x="Puntaje", rejilla="x")
guardar(fig, "g2_matriz_decision")
'''),
    analisis("¿El orden cambia si mueven los pesos o llenan los aranceles reales? Documenten qué fuente usaron para cada valor manual."),

    md("---\n# 10. Indicadores de impacto social\n\nLa ficha pide **al menos tres indicadores** (familias vinculadas, hectáreas sustituidas, ingresos generados) de Fedecacao, UNODC-SIMCI y la Agencia de Renovación del Territorio. No hay una descarga pública en formato de datos: la tabla es **editable** y el equipo la llena con la fuente y el año de cada cifra."),
    code('''
# ====================== EDITABLE: llenar con las cifras y su fuente ======================
IMPACTO = pd.DataFrame({
    "anio":                      [2018, 2020, 2022, 2024],
    "familias_vinculadas":       [np.nan, np.nan, np.nan, np.nan],
    "hectareas_sustituidas":     [np.nan, np.nan, np.nan, np.nan],
    "ingresos_generados_cop_mn": [np.nan, np.nan, np.nan, np.nan],
    "fuente":                    ["", "", "", ""],
})
# ==========================================================================================
exportar(IMPACTO, "g2_impacto_social")
IMPACTO
'''),
    code('''
indicadores = ["familias_vinculadas", "hectareas_sustituidas", "ingresos_generados_cop_mn"]
if IMPACTO[indicadores].notna().any().any():
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, ind, color in zip(axes, indicadores, CATEGORIAS):
        datos = IMPACTO.dropna(subset=[ind])
        ax.bar(datos["anio"].astype(str), datos[ind], color=color, width=0.6)
        for x, v in enumerate(datos[ind]):
            ax.annotate(f"{v:,.0f}", (x, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9, color=GRIS_TEXT)
        estilo(ax, ind.replace("_", " ").capitalize(), eje_y="")
    plt.tight_layout()
    guardar(fig, "g2_impacto_social")
else:
    print("La tabla IMPACTO esta vacia: llena al menos un indicador y vuelve a ejecutar esta celda.")
'''),
    analisis(),

    md("---\n# 11. Matrices estratégicas (DOFA, PESTEL, Cinco Fuerzas, benchmark)\n\nEstas matrices son cualitativas y no llevan código. El equipo las construye con las evidencias de las secciones anteriores.\n\n**DOFA del equipo:**\n\n_(escriban aquí)_\n\n**PESTEL del mercado priorizado:**\n\n_(escriban aquí)_\n\n**Cinco Fuerzas de Porter:**\n\n_(escriban aquí)_\n\n**Benchmark internacional (≥ 5 variables):**\n\n_(escriban aquí)_"),

    cierre([REF_BALASSA, REF_FAO, REF_BAENA]),
]

escribir(celdas, NB)
