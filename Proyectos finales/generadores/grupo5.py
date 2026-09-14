from comun import *

G = "Proyectos finales/Grupo 5"
D = G + "/datos/"
D2 = "Proyectos finales/Grupo 2/datos/"
NB = G + "/Grupo_5_Cacao_EUDR.ipynb"

ARCHIVOS = {
    "base":      D + "base_datos_cacao_eudr.xlsx",
    "exp_serie": D2 + "colombias-exports-to-world-by-importer_1801.csv",
    "exp_2025":  D2 + "colombias-exports-to-world-in-2025-by-importer_1801.csv",
    "imp_2025":  D2 + "colombias-imports-from-world-in-2025-by-exporter_1801.csv",
    "mundo_exp": D2 + "exporting-countries-in-2025_1801.csv",
    "mundo_imp": D2 + "importing-countries-in-2025_1801.csv",
    "canasta_co_exp":    "data/co_exp_productos_hs2_serie.xls",
    "canasta_co_imp":    "data/co_imp_productos_hs2_serie.csv",
    "canasta_mundo_exp": "data/mundo_exp_productos_hs2_serie.csv",
    "canasta_mundo_imp": "data/mundo_imp_productos_hs2_serie.csv",
}

METR = [
    ("Desempeño exportador: valor, volumen, CAGR", "¿Cuánto y a qué ritmo crece la exportación de cacao en grano?"),
    ("Ranking mundial de exportadores e importadores", "¿Dónde está Colombia y qué tan concentrados están los grandes?"),
    ("Concentración de destinos: HHI y Top 3/5/10", "¿Qué tan riesgosa es la cartera de destinos?"),
    ("Competitividad: RCA, RXA, RMA, RTA, RC y tasa de cobertura", "¿La ventaja es de exportación pura o hay importaciones que la matizan?"),
    ("Mercados de la Unión Europea", "¿Cuáles países de la UE importan más cacao y cuánto de eso es colombiano?"),
    ("Precio implícito (USD/t)", "¿A qué valor unitario vende Colombia frente a los grandes exportadores?"),
    ("Diagnóstico y matriz de brechas EUDR", "¿Qué tan preparado está el sector para el reglamento europeo?"),
]

celdas = [
    badge(NB),
    portada("Grupo 5. Cacao fino de aroma colombiano frente al EUDR: trazabilidad como argumento premium",
            "Grupo 5", "Cacao en grano, **HS 1801** (foco analítico); derivados 1803, 1804 y 1806 solo como referencia",
            "¿Cómo pueden los exportadores colombianos de cacao fino de aroma, en particular cooperativas y pequeños productores, cumplir de forma costo-eficiente la trazabilidad y geolocalización que exige el EUDR para no perder el mercado europeo y convertir el cumplimiento en diferenciación premium?",
            METR, "*Equipo 5 — Ficha técnica* (versión completa, septiembre de 2026) y su `base_datos_cacao_eudr.xlsx`. Las tablas de Trade Map por destino y los totales que la hoja `Datos_faltantes` marca como pendientes se tomaron de la carpeta del grupo 2 (mismo producto) y de la canasta del curso."),
    md("---\n# 0. Preparación del entorno"),
    CELL_IMPORTS,
    cell_config(G, ARCHIVOS),
    CELL_DESCARGA,
    CELL_LECTORES,
    cell_metricas(["hhi", "cr", "ibcr", "rca", "vollrath", "cagr"]),

    md("---\n# 1. Los datos\n\nEl Excel del equipo tiene nueve hojas con encabezado en la fila 4 (tres filas de título y fuente antes). Se leen las cuatro que tienen datos tabulares. Trampas: la hoja `Serie_nacional_Colombia` **mezcla** cifras de solo grano (HS 1801) con cacao y derivados (HS 18) y le falta 2022; los volúmenes traen coma de miles y los faltantes son un guion."),
    code('''
def leer_hoja(nombre, filas_antes=3):
    """Lee una hoja del Excel del equipo saltando las filas de titulo y fuente."""
    return pd.read_excel(ruta("base"), sheet_name=nombre, header=filas_antes)

exportadores_eq = leer_hoja("Exportadores_2025")
importadores_eq = leer_hoja("Importadores_2025")
serie_nacional  = leer_hoja("Serie_nacional_Colombia")
diagnostico     = leer_hoja("Diagnostico_EUDR_Colombia")
for tabla in (exportadores_eq, importadores_eq):
    for col in tabla.columns[2:]:
        tabla[col] = a_numero(tabla[col])
serie_nacional["Año"] = pd.to_numeric(serie_nacional["Año"], errors="coerce")
serie_nacional = serie_nacional.dropna(subset=["Año"]).astype({"Año": int})
serie_nacional["valor_usd_mn"] = a_numero(serie_nacional["Valor exportado (US$ M)"])
serie_nacional["volumen_t"] = a_numero(serie_nacional["Volumen (Toneladas)"])
print(exportadores_eq.columns.tolist())
serie_nacional
'''),
    code('''
serie     = leer_serie_trademap(ruta("exp_serie"))
exp_2025  = leer_trademap(ruta("exp_2025"))
imp_2025  = leer_trademap(ruta("imp_2025"))
mundo_exp = leer_trademap(ruta("mundo_exp"))
mundo_imp = leer_trademap(ruta("mundo_imp"))
canastas = {k: leer_canasta(ruta(k)) for k in ("canasta_co_exp", "canasta_co_imp", "canasta_mundo_exp", "canasta_mundo_imp")}

mundo_2025, destinos_2025 = separar_mundo(exp_2025)
mundo_imp_2025, _ = separar_mundo(imp_2025)
mundo_oferta, exportadores = separar_mundo(mundo_exp)
mundo_demanda, importadores = separar_mundo(mundo_imp)
print(f"Colombia exporto cacao en grano por USD {mundo_2025['valor_kusd']:,.0f} miles ({mundo_2025['cantidad']:,.0f} t) en 2025 a {len(destinos_2025)} destinos")
print(f"Colombia importo cacao en grano por USD {mundo_imp_2025['valor_kusd']:,.0f} miles")
'''),

    md("---\n# 2. Desempeño exportador: valor, volumen y CAGR\n\nSe muestran las dos series: la **homogénea** de Trade Map (solo HS 1801, 2016-2025) y la **mixta** que el equipo compiló en `Serie_nacional_Colombia`. El CAGR se calcula sobre ambas para que el equipo vea la diferencia."),
    code('''
total = serie[serie["codigo"] == "000"].set_index("anio")["valor_kusd"]
desempeno = pd.DataFrame({"trade_map_hs1801_usd_mn": total / 1000})
desempeno = desempeno.join(serie_nacional.set_index("Año")[["valor_usd_mn", "Alcance del dato", "volumen_t"]].rename(columns={"valor_usd_mn": "serie_equipo_usd_mn", "Alcance del dato": "alcance_serie_equipo"}))
print(f"CAGR 2021-2025 Trade Map HS 1801: {cagr(total[2021], total[2025], 4):.1f} %")
print(f"CAGR 2016-2025 Trade Map HS 1801: {cagr(total[2016], total[2025], 9):.1f} %")
eq = serie_nacional.dropna(subset=["valor_usd_mn"]).set_index("Año")["valor_usd_mn"]
print(f"CAGR {eq.index.min()}-{eq.index.max()} serie del equipo (mixta): {cagr(eq.iloc[0], eq.iloc[-1], eq.index.max() - eq.index.min()):.1f} %")
exportar(desempeno.reset_index(), "g5_desempeno")
desempeno
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
axes[0].bar(total.index.astype(str), total.values / 1000, color=AZUL, width=0.6, label="Trade Map, HS 1801")
axes[0].plot(eq.index.astype(str), eq.values, color=NARANJA, linewidth=2, marker="s", markersize=6, label="Serie del equipo (mezcla HS 1801 y HS 18)")
for x, v in enumerate(total.values / 1000):
    axes[0].annotate(f"{v:.0f}", (x, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8.5, color=GRIS_TEXT)
axes[0].legend(frameon=False, fontsize=9, loc="upper left")
estilo(axes[0], "Exportaciones colombianas de cacao", "Millones de USD", eje_y="USD millones")
vol = destinos_2025.nlargest(8, "cantidad")
axes[1].barh(vol["pais"][::-1], vol["cantidad"][::-1], color=VERDE, height=0.6)
for y, v in enumerate(vol["cantidad"][::-1]):
    axes[1].annotate(f"{v:,.0f} t", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(axes[1], "Volumen exportado por destino, 2025", "Toneladas, ocho mayores", "Trade Map (ITC), 2025; base de datos del equipo.", eje_x="t", rejilla="x")
plt.tight_layout()
guardar(fig, "g5_desempeno")
'''),
    analisis("¿Por qué el CAGR de la serie mixta y el de la serie homogénea son tan distintos? ¿Cuál debe ir en el informe?"),

    md("---\n# 3. Ranking mundial de exportadores e importadores, 2025\n\nDesde las hojas del equipo. La columna `Índice concentración (HHI)` la calcula Trade Map para cada país: mide cuán concentrados están **sus** socios."),
    code('''
COMPARADORES = ["Colombia", "Côte d'Ivoire", "Ecuador", "Ghana", "Perú"]
top_exp = exportadores_eq.nlargest(12, "Valor (kUSD)")
top_exp = pd.concat([top_exp, exportadores_eq[exportadores_eq["País"].isin(COMPARADORES) & ~exportadores_eq["País"].isin(top_exp["País"])]]).drop_duplicates("País")
top_imp = importadores_eq.nlargest(12, "Valor (kUSD)")
exportar(top_exp, "g5_ranking_exportadores"); exportar(top_imp, "g5_ranking_importadores")
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
for ax, tabla, titulo in zip(axes, (top_exp, top_imp), ("Exportadores", "Importadores")):
    orden = tabla.sort_values("Participación mundial (%)")
    colores = [NARANJA if p == "Colombia" else (AZUL if p in COMPARADORES else GRIS_MID) for p in orden["País"]]
    ax.barh(orden["País"], orden["Participación mundial (%)"], color=colores, height=0.6)
    for y, v in enumerate(orden["Participación mundial (%)"]):
        ax.annotate(f"{v:.2f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
    estilo(ax, f"{titulo} mundiales de cacao en grano, 2025", "% del valor mundial", eje_x="%", rejilla="x")
fig.text(0.01, -0.03, "Fuente: Trade Map (ITC), 2025, vía base de datos del equipo. Naranja = Colombia; azul = competidores de la ficha.", fontsize=8, color=GRIS_EJE)
plt.tight_layout()
guardar(fig, "g5_rankings")
'''),
    code('''
hhi_paises = exportadores_eq[exportadores_eq["País"].isin(COMPARADORES)][["País", "Valor (kUSD)", "Participación mundial (%)", "Índice concentración (HHI)"]].sort_values("Índice concentración (HHI)")
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.barh(hhi_paises["País"], hhi_paises["Índice concentración (HHI)"], color=[NARANJA if p == "Colombia" else AZUL for p in hhi_paises["País"]], height=0.55)
for y, v in enumerate(hhi_paises["Índice concentración (HHI)"]):
    ax.annotate(f"{v:.4f}", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Concentración de destinos según Trade Map: Colombia frente a sus competidores, 2025", "HHI de los socios de cada exportador", "Trade Map (ITC), 2025.", eje_x="HHI", rejilla="x")
guardar(fig, "g5_hhi_competidores")
exportar(hhi_paises, "g5_hhi_competidores")
'''),
    analisis(),

    md("---\n# 4. Concentración de destinos: HHI, Top 3/5/10 y mapa de riesgo de cartera"),
    code('''
paises_serie = serie[serie["codigo"] != "000"]
concentracion = (paises_serie.groupby("anio")["valor_kusd"]
                 .agg(HHI=hhi, Top3=lambda v: cr_n(v, 3), Top5=lambda v: cr_n(v, 5), Top10=lambda v: cr_n(v, 10), destinos_activos=lambda v: int((v > 0).sum()))
                 .reset_index())
concentracion["numero_equivalente"] = numeros_equivalentes(concentracion["HHI"])
exportar(concentracion, "g5_concentracion")
concentracion
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(concentracion["anio"], concentracion["HHI"], color=AZUL, linewidth=2.4, marker="o", markersize=7)
for _, f in concentracion.iterrows():
    axes[0].annotate(f"{f['HHI']:.3f}", (f["anio"], f["HHI"]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].axhspan(0.18, 1, color=ROJO, alpha=0.06)
axes[0].axhspan(0.15, 0.18, color=NARANJA, alpha=0.06)
axes[0].set_ylim(0, max(0.6, concentracion["HHI"].max() * 1.2))
axes[0].set_xticks(concentracion["anio"])
estilo(axes[0], "HHI de destinos del cacao colombiano", "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", eje_y="HHI")
cartera = destinos_2025.nlargest(10, "valor_kusd").copy()
cartera["acumulado_pct"] = cartera["participacion_pct"].cumsum()
axes[1].bar(cartera["pais"], cartera["participacion_pct"], color=AZUL, width=0.6, label="Participación")
axes[1].plot(cartera["pais"], cartera["acumulado_pct"], color=NARANJA, linewidth=2, marker="o", markersize=5, label="Acumulado")
for x, v in enumerate(cartera["acumulado_pct"]):
    axes[1].annotate(f"{v:.0f} %", (x, v), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8.5, color=GRIS_TEXT)
axes[1].set_ylim(0, 110)
axes[1].tick_params(axis="x", rotation=45, labelsize=8)
axes[1].legend(frameon=False, fontsize=9, loc="center right")
estilo(axes[1], "Mapa de riesgo de cartera, 2025", "Participación de los diez mayores destinos y acumulado (Top 3 / 5 / 10)", "Trade Map (ITC), 2025.", eje_y="%")
plt.tight_layout()
guardar(fig, "g5_concentracion")
'''),
    analisis(),

    md("---\n# 5. Competitividad: Balassa y la familia de Vollrath\n\nRXA, RMA, RTA y RC excluyen al propio país y al propio producto del denominador (Vollrath, 1991). Se necesitan ocho cifras: exportaciones e importaciones de cacao de Colombia y del mundo (Trade Map, 2025) y las totales de Colombia y del mundo (fila TOTAL de las cuatro canastas HS2 del curso). La tasa de cobertura (TC) es X / M del producto."),
    code('''
X_ij, M_ij = mundo_2025["valor_kusd"], mundo_imp_2025["valor_kusd"]
X_j,  M_j  = mundo_oferta["valor_kusd"], mundo_demanda["valor_kusd"]
X_i  = fila_canasta(canastas["canasta_co_exp"], "TOTAL")["2025"]
M_i  = fila_canasta(canastas["canasta_co_imp"], "TOTAL")["2025"]
X_w  = fila_canasta(canastas["canasta_mundo_exp"], "TOTAL")["2025"]
M_w  = fila_canasta(canastas["canasta_mundo_imp"], "TOTAL")["2025"]
rca = float(rca_balassa(X_ij, X_i, X_j, X_w))
voll = indices_vollrath(X_ij, M_ij, X_j, M_j, X_i, M_i, X_w, M_w)
competitividad = pd.DataFrame({
    "indice": ["RCA (Balassa)", "RSCA (Laursen)", "RXA (Vollrath)", "RMA (Vollrath)", "RTA = RXA - RMA", "RC = ln RXA - ln RMA", "TC = X / M", "IBCR = (X-M)/(X+M)"],
    "valor": [rca, float(rsca_laursen(rca)), voll["RXA"], voll["RMA"], voll["RTA"], voll["RC"], X_ij / M_ij, float(ibcr(X_ij, M_ij))],
    "umbral_neutral": [1, 0, 1, 1, 0, 0, 1, 0],
})
print(f"X_ij={X_ij:,.0f} M_ij={M_ij:,.0f} X_j={X_j:,.0f} M_j={M_j:,.0f} X_i={X_i:,.0f} M_i={M_i:,.0f} X_w={X_w:,.0f} M_w={M_w:,.0f}  (USD miles, 2025)")
exportar(competitividad, "g5_competitividad")
competitividad
'''),
    code('''
vcr_cap18 = pd.DataFrame({"anio": [int(a) for a in ANIOS_CANASTA]})
vcr_cap18["RCA_cap18"] = rca_balassa(fila_canasta(canastas["canasta_co_exp"], "18"), fila_canasta(canastas["canasta_co_exp"], "TOTAL"),
                                     fila_canasta(canastas["canasta_mundo_exp"], "18"), fila_canasta(canastas["canasta_mundo_exp"], "TOTAL"))
exportar(vcr_cap18, "g5_rca_cap18")
fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
sim = competitividad[competitividad["indice"].isin(["RSCA (Laursen)", "RTA = RXA - RMA", "RC = ln RXA - ln RMA", "IBCR = (X-M)/(X+M)"])]
axes[0].bar(sim["indice"].str.split(" ").str[0], sim["valor"], color=[ROJO if v < 0 else AZUL for v in sim["valor"]], width=0.55)
for x, v in enumerate(sim["valor"]):
    axes[0].annotate(f"{v:+.2f}", (x, v), textcoords="offset points", xytext=(0, 5 if v >= 0 else -12), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].axhline(0, color=GRIS_EJE, linewidth=0.8)
estilo(axes[0], "Índices simétricos de ventaja comparativa, HS 1801, 2025", "0 = neutral; positivo = ventaja", eje_y="valor")
axes[1].plot(vcr_cap18["anio"], vcr_cap18["RCA_cap18"], color=VERDE, linewidth=2.2, marker="o", markersize=6, label="Capítulo 18")
axes[1].scatter([2025], [rca], color=AZUL, s=70, zorder=3, label="HS 1801, 2025")
for _, f in vcr_cap18.iterrows():
    axes[1].annotate(f"{f['RCA_cap18']:.2f}", (f["anio"], f["RCA_cap18"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].axhline(1, color=GRIS_EJE, linewidth=0.8, linestyle="--")
axes[1].set_xticks(vcr_cap18["anio"])
axes[1].set_ylim(0, max(vcr_cap18["RCA_cap18"].max(), rca) * 1.3)
axes[1].legend(frameon=False, fontsize=9, loc="upper left")
estilo(axes[1], "RCA de Balassa, 2021-2025", "Línea punteada = 1", "Trade Map (ITC), 2025; canasta HS2 del curso.", eje_y="RCA")
plt.tight_layout()
guardar(fig, "g5_competitividad")
'''),
    analisis("¿Qué agrega RXA/RMA frente al RCA de Balassa en este caso? ¿Qué dice el RMA tan bajo?"),

    md("---\n# 6. Mercados de la Unión Europea\n\nImportaciones de cacao en grano de cada país de la UE (Trade Map, 2025) y cuota de Colombia en cada uno."),
    code('''
UE27 = ["Alemania", "Austria", "Bélgica", "Bulgaria", "Chipre", "Croacia", "Dinamarca", "Eslovaquia", "Eslovenia", "España", "Estonia", "Finlandia", "Francia", "Grecia", "Hungría", "Irlanda", "Italia", "Letonia", "Lituania", "Luxemburgo", "Malta", "Países Bajos", "Polonia", "Portugal", "República Checa", "Rumania", "Suecia"]
ue = importadores[importadores["pais"].isin(UE27)][["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_mundial_pct", "crec_valor_5a_pct", "crec_valor_2a_pct"]]
ue = ue.merge(destinos_2025[["pais", "valor_kusd", "cuota_en_socio_pct", "ranking_socio"]].rename(columns={"valor_kusd": "colombia_exporta_kusd"}), on="pais", how="left")
ue["cuota_en_socio_pct"] = ue["cuota_en_socio_pct"].fillna(0)
ue = ue.sort_values("valor_kusd", ascending=False).head(12)
print(f"La UE importa cacao en grano por USD {importadores[importadores['pais'].isin(UE27)]['valor_kusd'].sum():,.0f} miles; Colombia le vende USD {ue['colombia_exporta_kusd'].sum():,.0f} miles")
exportar(ue, "g5_mercados_ue")
ue
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
orden = ue.sort_values("valor_kusd")
axes[0].barh(orden["pais"], orden["valor_kusd"], color=AZUL, height=0.6)
for y, (v, g) in enumerate(zip(orden["valor_kusd"], orden["crec_valor_5a_pct"])):
    axes[0].annotate(f"{fmt_miles(v)}  crec. 5 años {g:+.0f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=8.5, color=GRIS_TEXT)
axes[0].xaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
axes[0].set_xlim(0, orden["valor_kusd"].max() * 1.5)
estilo(axes[0], "Importaciones de cacao en grano por país de la UE, 2025", "Doce mayores; USD", eje_x="USD", rejilla="x")
orden = ue.sort_values("cuota_en_socio_pct")
axes[1].barh(orden["pais"], orden["cuota_en_socio_pct"], color=NARANJA, height=0.6)
for y, v in enumerate(orden["cuota_en_socio_pct"]):
    axes[1].annotate(f"{v:.2f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(axes[1], "Cuota de Colombia en las importaciones de cada país", "% de sus importaciones de HS 1801", "Trade Map (ITC), 2025.", eje_x="%", rejilla="x")
plt.tight_layout()
guardar(fig, "g5_mercados_ue")
'''),
    analisis("¿Países Bajos y Bélgica son consumo o puerta de entrada? ¿Qué implica para la trazabilidad EUDR?"),

    md("---\n# 7. Precio implícito: valor unitario de exportación"),
    code('''
precios = exportadores.nlargest(10, "valor_kusd")
precios = pd.concat([precios, exportadores[exportadores["pais"].isin(COMPARADORES)]]).drop_duplicates("pais")
precios = precios[precios["cantidad"] > 0][["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_mundial_pct"]].sort_values("valor_unitario")
fig, ax = plt.subplots(figsize=(9, 5.5))
colores = [NARANJA if p == "Colombia" else (AZUL if p in COMPARADORES else GRIS_MID) for p in precios["pais"]]
ax.barh(precios["pais"], precios["valor_unitario"], color=colores, height=0.6)
ax.axvline(mundo_oferta["valor_unitario"], color=GRIS_EJE, linewidth=1.2, linestyle="--")
ax.annotate(f"promedio mundial {mundo_oferta['valor_unitario']:,.0f}", (mundo_oferta["valor_unitario"], len(precios) - 0.4), xytext=(4, 0), textcoords="offset points", fontsize=9, color=GRIS_TEXT)
for y, v in enumerate(precios["valor_unitario"]):
    ax.annotate(f"{v:,.0f}", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
estilo(ax, "Valor unitario de exportación de cacao en grano, 2025", "USD por tonelada; diez mayores exportadores y competidores de la ficha", "Trade Map (ITC), 2025.", eje_x="USD/t", rejilla="x")
guardar(fig, "g5_precio_implicito")
exportar(precios, "g5_precio_implicito")
'''),
    analisis("El valor unitario no es el precio del cacao fino de aroma, pero ¿qué sugiere la posición de Colombia?"),

    md("---\n# 8. Diagnóstico y matriz de brechas EUDR\n\nPrimero los indicadores que el equipo ya encontró (hoja `Diagnostico_EUDR_Colombia`, con el referente del café). Después la **matriz de brechas** de la ficha, con los seis KPI en una tabla **editable**: el equipo llena el valor actual y la meta de cada uno."),
    code('''
diag = diagnostico.dropna(subset=["Indicador"]).copy()
diag["valor_pct"] = np.where(diag["Valor"].astype(str).str.contains("%"), a_numero(diag["Valor"]), np.nan)
diag_pct = diag.dropna(subset=["valor_pct"])
exportar(diag, "g5_diagnostico_eudr")
fig, ax = plt.subplots(figsize=(10, 4.5))
colores = [NARANJA if "afé" in str(s) else AZUL for s in diag_pct["Sector"]]
etiquetas = [f"{i[:60]}  [{s}]" for i, s in zip(diag_pct["Indicador"], diag_pct["Sector"])]
ax.barh(etiquetas[::-1], diag_pct["valor_pct"][::-1], color=colores[::-1], height=0.6)
for y, v in enumerate(diag_pct["valor_pct"][::-1]):
    ax.annotate(f"{v:.0f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.set_xlim(0, 110)
estilo(ax, "Diagnóstico de preparación EUDR: indicadores encontrados", "Azul = cacao; naranja = referente del café", "Base de datos del equipo (USDA FAS, Fedecacao, FNC).", eje_x="%", rejilla="x")
guardar(fig, "g5_diagnostico_eudr")
diag[["Indicador", "Valor", "Sector", "Fuente"]]
'''),
    code('''
# ====================== EDITABLE: matriz de brechas EUDR (valor actual y meta, en %) ======================
BRECHAS = pd.DataFrame({
    "kpi": ["% predios con coordenadas validadas", "% lotes con screening satelital", "% predios con expediente legal completo",
            "% lotes con ID único / trazabilidad", "% evidencias de cero deforestación completas", "% registros auditables"],
    "requisito_eudr": ["Geolocalización", "Cero deforestación", "Legalidad", "Trazabilidad", "Cero deforestación", "Trazabilidad"],
    "valor_actual_pct": [72, 9, np.nan, np.nan, np.nan, np.nan],
    "meta_2026_pct":    [100, 100, 100, 100, 100, 100],
    "fuente": ["USDA FAS 2024", "Base del equipo", "", "", "", ""],
})
# ==========================================================================================================
BRECHAS["brecha_pct"] = BRECHAS["meta_2026_pct"] - BRECHAS["valor_actual_pct"]
exportar(BRECHAS, "g5_matriz_brechas")
con_dato = BRECHAS.dropna(subset=["valor_actual_pct"])
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.barh(con_dato["kpi"][::-1], con_dato["meta_2026_pct"][::-1], color=REJILLA, height=0.6, label="Meta")
ax.barh(con_dato["kpi"][::-1], con_dato["valor_actual_pct"][::-1], color=AZUL, height=0.6, label="Valor actual")
for y, (v, b) in enumerate(zip(con_dato["valor_actual_pct"][::-1], con_dato["brecha_pct"][::-1])):
    ax.annotate(f"{v:.0f} %  (brecha {b:.0f} pp)", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.set_xlim(0, 115)
ax.legend(frameon=False, fontsize=9, loc="lower right")
estilo(ax, "Matriz de brechas EUDR", "KPI con dato; los demás se llenan en la celda editable", "Elaboración del equipo.", eje_x="%", rejilla="x")
guardar(fig, "g5_matriz_brechas")
BRECHAS
'''),
    analisis("¿Cuáles KPI son críticos antes del 30 de diciembre de 2026 y cuáles pueden esperar a la declaración simplificada de junio de 2027?"),

    md("---\n# 9. Benchmarking\n\nLa matriz benchmark (Colombia frente a Ecuador, Perú y el referente del café) es cualitativa y se construye con las evidencias anteriores. No lleva código.\n\n**Matriz benchmark del equipo:**\n\n_(escriban aquí)_"),

    cierre([REF_BALASSA, REF_VOLLRATH]),
]

escribir(celdas, NB)
