from comun import *

G = "Proyectos finales/Grupo 3"
D = G + "/datos/"
NB = G + "/Grupo_3_Cafe.ipynb"

ARCHIVOS = {
    "exp_serie": D + "colombias-exports-to-world-by-importer_090111.csv",
    "exp_2025":  D + "colombias-exports-to-world-in-2025-by-importer_090111.csv",
    "mundo_imp": D + "importing-countries-in-2025_090111.csv",
    "mundo_exp": D + "exporting-countries-in-2025_090111.csv",
    "prov_alemania": D + "germanys-imports-from-world-in-2025-by-exporter_090111.csv",
    "prov_japon":    D + "japans-imports-from-world-in-2025-by-exporter_090111.csv",
    "prov_corea":    D + "koreas-imports-from-world-in-2025-by-exporter_090111.csv",
}

METR = [
    ("Participación por destino y evolución 2016-2025", "¿Cuánto pesa Estados Unidos y cuánto pesan Alemania, Japón y Corea del Sur?"),
    ("CR4 y HHI de destinos", "¿Qué tan concentrado está el café verde colombiano en pocos mercados?"),
    ("Tamaño y crecimiento de los mercados importadores", "¿Cuánto café verde importa cada candidato y a qué ritmo crece?"),
    ("Proveedores de cada mercado candidato", "¿Contra quién compite Colombia en Alemania, Japón y Corea (Brasil, Vietnam)?"),
    ("Matriz comparativa de los tres destinos", "¿Cómo se comparan en participación, crecimiento, tamaño, acceso y competencia?"),
    ("Escenarios de diversificación", "¿Cuánto bajaría la dependencia de Estados Unidos si los tres mercados crecen como en la ficha?"),
]

celdas = [
    badge(NB),
    portada("Grupo 3. Diversificar o depender: la decisión que le falta al café colombiano",
            "Grupo 3", "Café verde sin tostar ni descafeinar, **HS 090111**",
            "¿Cuál es el potencial de Alemania, Japón y Corea del Sur como mercados alternativos a Estados Unidos para el café verde colombiano, y qué estrategia de diversificación reduce la dependencia de un solo destino?",
            METR, "*Equipo 3 — Ficha técnica* (septiembre de 2026). Las descargas de Trade Map que sustentan las cifras de la ficha se hicieron para este cuaderno y están en `datos/`."),
    md("---\n# 0. Preparación del entorno"),
    CELL_IMPORTS,
    cell_config(G, ARCHIVOS),
    CELL_DESCARGA,
    CELL_LECTORES,
    cell_metricas(["hhi", "cr", "cagr"]),

    md("---\n# 1. Los datos\n\nSiete tablas de Trade Map para HS 090111: la serie de Colombia por destino (2016-2025), el corte 2025 con indicadores, los importadores y exportadores del mundo, y los proveedores de Alemania, Japón y Corea del Sur."),
    code('''
serie     = leer_serie_trademap(ruta("exp_serie"))
exp_2025  = leer_trademap(ruta("exp_2025"))
mundo_imp = leer_trademap(ruta("mundo_imp"))
mundo_exp = leer_trademap(ruta("mundo_exp"))
proveedores = {
    "Alemania": leer_trademap(ruta("prov_alemania")),
    "Japón": leer_trademap(ruta("prov_japon")),
    "Corea del Sur": leer_trademap(ruta("prov_corea")),
}
CANDIDATOS = {"Alemania": "Alemania", "Japón": "Japón", "Corea del Sur": "Corea, República de"}   # nombre corto -> nombre en Trade Map
EEUU = "Estados Unidos de América"

mundo_2025, destinos_2025 = separar_mundo(exp_2025)
mundo_demanda, importadores = separar_mundo(mundo_imp)
mundo_oferta, exportadores = separar_mundo(mundo_exp)
print(f"Colombia exporto cafe verde por USD {mundo_2025['valor_kusd']:,.0f} miles en 2025 a {len(destinos_2025)} destinos")
destinos_2025[["pais", "valor_kusd", "participacion_pct", "cuota_en_socio_pct", "ranking_socio", "crec_valor_5a_pct", "crec_valor_2a_pct"]].head(10)
'''),

    md("---\n# 2. Participación por destino y evolución, 2016-2025"),
    code('''
paises_serie = serie[serie["codigo"] != "000"]
FOCO = [EEUU] + list(CANDIDATOS.values())
series_foco = (paises_serie.assign(grupo=lambda d: np.where(d["pais"].isin(FOCO), d["pais"], "Otros"))
                           .groupby(["anio", "grupo"])["valor_kusd"].sum().unstack("grupo")[FOCO + ["Otros"]])
participacion_foco = series_foco.div(series_foco.sum(axis=1), axis=0) * 100
exportar(participacion_foco.reset_index(), "g3_participacion_serie")
participacion_foco.round(2)
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colores = CATEGORIAS + [GRIS_MID]
for color, columna in zip(colores, series_foco.columns):
    axes[0].plot(series_foco.index, series_foco[columna], color=color, linewidth=2.2, marker="o", markersize=5, label=columna)
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
axes[0].set_xticks(series_foco.index)
axes[0].legend(frameon=False, fontsize=9, loc="upper left")
estilo(axes[0], "Valor exportado por destino", "USD; Estados Unidos, los tres candidatos y el resto", eje_y="USD")

axes[1].stackplot(participacion_foco.index, [participacion_foco[c] for c in participacion_foco.columns], colors=colores, labels=participacion_foco.columns, alpha=0.9)
axes[1].set_ylim(0, 100)
axes[1].set_xticks(participacion_foco.index)
estilo(axes[1], "Participación de cada destino", "% del valor exportado cada año", "Trade Map (ITC), 2025.", eje_y="%")
plt.tight_layout()
guardar(fig, "g3_participacion_serie")
'''),
    code('''
# Crecimiento reciente por destino: CAGR 2016-2025, 2020-2025 y variacion 2024-2025
ancho = paises_serie.pivot(index="pais", columns="anio", values="valor_kusd")
top12 = ancho[2025].nlargest(12).index
crecimiento = pd.DataFrame({
    "valor_2025": ancho.loc[top12, 2025],
    "participacion_2025_pct": ancho.loc[top12, 2025] / ancho[2025].sum() * 100,
    "cagr_2016_2025_pct": [cagr(ancho.loc[p, 2016], ancho.loc[p, 2025], 9) for p in top12],
    "cagr_2020_2025_pct": [cagr(ancho.loc[p, 2020], ancho.loc[p, 2025], 5) for p in top12],
    "variacion_2024_2025_pct": (ancho.loc[top12, 2025] / ancho.loc[top12, 2024] - 1) * 100,
}).reset_index()
exportar(crecimiento, "g3_crecimiento_destinos")
crecimiento
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 5.5))
orden = crecimiento.sort_values("cagr_2020_2025_pct")
colores = [NARANJA if p in FOCO else GRIS_MID for p in orden["pais"]]
ax.barh(orden["pais"], orden["cagr_2020_2025_pct"], color=colores, height=0.6)
for y, v in enumerate(orden["cagr_2020_2025_pct"]):
    ax.annotate(f"{v:+.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
ax.axvline(0, color=GRIS_EJE, linewidth=0.8)
estilo(ax, "Crecimiento anual compuesto de las exportaciones por destino, 2020-2025", "Doce mayores destinos; en naranja Estados Unidos y los tres candidatos",
       "Trade Map (ITC), 2025.", eje_x="CAGR (%)", rejilla="x")
guardar(fig, "g3_crecimiento_destinos")
'''),
    analisis("¿Los tres candidatos crecen más rápido que Estados Unidos? ¿Desde qué año?"),

    md("---\n# 3. Concentración: CR4 y HHI de destinos"),
    code('''
concentracion = (paises_serie.groupby("anio")["valor_kusd"]
                 .agg(HHI=hhi, CR4=lambda v: cr_n(v, 4), CR1=lambda v: cr_n(v, 1), destinos_activos=lambda v: int((v > 0).sum()))
                 .reset_index())
concentracion["numero_equivalente"] = numeros_equivalentes(concentracion["HHI"])
exportar(concentracion, "g3_concentracion")
concentracion
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
axes[0].plot(concentracion["anio"], concentracion["CR4"], color=AZUL, linewidth=2.4, marker="o", markersize=7, label="CR4 (cuatro mayores)")
axes[0].plot(concentracion["anio"], concentracion["CR1"], color=NARANJA, linewidth=2.4, marker="o", markersize=7, label="CR1 (el mayor: Estados Unidos)")
for _, fila in concentracion.iterrows():
    axes[0].annotate(f"{fila['CR4']:.0f}", (fila["anio"], fila["CR4"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
    axes[0].annotate(f"{fila['CR1']:.0f}", (fila["anio"], fila["CR1"]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color=GRIS_TEXT)
axes[0].set_ylim(0, 105)
axes[0].set_xticks(concentracion["anio"])
axes[0].legend(frameon=False, fontsize=9, loc="lower left")
estilo(axes[0], "Razones de concentración de destinos", "% del valor exportado", eje_y="%")

axes[1].plot(concentracion["anio"], concentracion["HHI"], color=VERDE, linewidth=2.4, marker="o", markersize=7)
for _, fila in concentracion.iterrows():
    axes[1].annotate(f"{fila['HHI']:.3f}", (fila["anio"], fila["HHI"]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=GRIS_TEXT)
axes[1].axhspan(0.18, 1, color=ROJO, alpha=0.06)
axes[1].axhspan(0.15, 0.18, color=NARANJA, alpha=0.06)
axes[1].set_ylim(0, max(0.4, concentracion["HHI"].max() * 1.25))
axes[1].set_xticks(concentracion["anio"])
estilo(axes[1], "HHI de destinos", "Bandas: > 0,18 concentrado; 0,15-0,18 moderado; < 0,15 fragmentado", "Trade Map (ITC), 2025.", eje_y="HHI")
plt.tight_layout()
guardar(fig, "g3_concentracion")
'''),
    analisis(),

    md("---\n# 4. Tamaño y crecimiento de los mercados importadores"),
    code('''
demanda = importadores.nlargest(15, "valor_kusd")[["pais", "valor_kusd", "cantidad", "valor_unitario", "participacion_mundial_pct", "crec_valor_5a_pct", "crec_valor_2a_pct"]]
demanda = demanda.merge(destinos_2025[["pais", "cuota_en_socio_pct", "ranking_socio"]], on="pais", how="left")
exportar(demanda, "g3_mercados_importadores")
fig, ax = plt.subplots(figsize=(9, 6))
orden = demanda.sort_values("valor_kusd")
colores = [NARANJA if p in FOCO else GRIS_MID for p in orden["pais"]]
ax.barh(orden["pais"], orden["valor_kusd"], color=colores, height=0.6)
for y, (v, g, c) in enumerate(zip(orden["valor_kusd"], orden["crec_valor_5a_pct"], orden["cuota_en_socio_pct"])):
    ax.annotate(f"crec. 5 años {g:+.0f} %  |  cuota de Colombia {c:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=8.5, color=GRIS_TEXT)
ax.xaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
ax.set_xlim(0, orden["valor_kusd"].max() * 1.6)
estilo(ax, "Quince mayores importadores de café verde del mundo, 2025", "Valor importado (USD); en naranja Estados Unidos y los tres candidatos",
       "Trade Map (ITC), 2025.", eje_x="USD", rejilla="x")
guardar(fig, "g3_mercados_importadores")
demanda
'''),
    analisis(),

    md("---\n# 5. Proveedores de cada mercado candidato"),
    code('''
cuadros = {}
for nombre, tabla in proveedores.items():
    total, paises = separar_mundo(tabla)
    top = paises.nlargest(8, "valor_kusd")[["pais", "valor_kusd", "participacion_pct", "crec_valor_5a_pct", "valor_unitario"]]
    if "Colombia" not in top["pais"].values:
        top = pd.concat([top, paises[paises["pais"] == "Colombia"][top.columns]])
    top.insert(0, "mercado", nombre)
    cuadros[nombre] = top
tabla_proveedores = pd.concat(cuadros.values(), ignore_index=True)
exportar(tabla_proveedores, "g3_proveedores")
tabla_proveedores
'''),
    code('''
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
for ax, (nombre, top) in zip(axes, cuadros.items()):
    orden = top.sort_values("participacion_pct")
    colores = [NARANJA if p == "Colombia" else (AZUL if p in ("Brasil", "Viet Nam") else GRIS_MID) for p in orden["pais"]]
    ax.barh(orden["pais"], orden["participacion_pct"], color=colores, height=0.6)
    for y, v in enumerate(orden["participacion_pct"]):
        ax.annotate(f"{v:.1f} %", (v, y), textcoords="offset points", xytext=(4, 0), va="center", fontsize=9, color=GRIS_TEXT)
    ax.set_xlim(0, orden["participacion_pct"].max() * 1.25)
    estilo(ax, f"Proveedores de {nombre}", "% de sus importaciones de café verde, 2025", eje_x="%", rejilla="x")
axes[2].figure.text(0.01, -0.03, "Fuente: Trade Map (ITC), 2025. Naranja = Colombia; azul = Brasil y Vietnam.", fontsize=8, color=GRIS_EJE)
plt.tight_layout()
guardar(fig, "g3_proveedores")
'''),
    analisis("¿Qué posición ocupa Colombia en cada mercado y qué tan lejos está del líder?"),

    md("---\n# 6. Matriz comparativa de los tres destinos\n\nLos tres bloques de la ficha (participación y crecimiento; acceso y tamaño; competencia y diferenciación). Las columnas de **arancel y condiciones de acceso** son editables porque salen de Legiscomex, no de Trade Map."),
    code('''
# ====================== EDITABLE: arancel y acceso, desde Legiscomex ======================
ACCESO = pd.DataFrame({
    "arancel_nmf_cafe_verde_pct": [np.nan, np.nan, np.nan],
    "arancel_colombia_pct":       [np.nan, np.nan, np.nan],
    "condiciones_de_acceso":      ["", "", ""],
}, index=list(CANDIDATOS.keys()))
# ===========================================================================================

filas = []
for nombre, etiqueta in CANDIDATOS.items():
    d = destinos_2025.set_index("pais").loc[etiqueta]
    m = importadores.set_index("pais").loc[etiqueta]
    lider = separar_mundo(proveedores[nombre])[1].nlargest(1, "valor_kusd").iloc[0]
    filas.append({
        "mercado": nombre,
        # 6.1 participacion y crecimiento
        "exportaciones_colombia_2025_kusd": d["valor_kusd"],
        "participacion_en_exp_colombia_pct": d["participacion_pct"],
        "cagr_2016_2025_pct": cagr(ancho.loc[etiqueta, 2016], ancho.loc[etiqueta, 2025], 9),
        "variacion_2024_2025_pct": (ancho.loc[etiqueta, 2025] / ancho.loc[etiqueta, 2024] - 1) * 100,
        # 6.2 tamano del mercado y acceso
        "importaciones_totales_2025_kusd": m["valor_kusd"],
        "crec_importaciones_5a_pct": m["crec_valor_5a_pct"],
        "precio_importacion_usd_t": m["valor_unitario"],
        # 6.3 competencia
        "cuota_colombia_pct": d["cuota_en_socio_pct"],
        "puesto_colombia": d["ranking_socio"],
        "proveedor_lider": lider["pais"],
        "cuota_lider_pct": lider["participacion_pct"],
    })
matriz = pd.DataFrame(filas).set_index("mercado").join(ACCESO)
exportar(matriz.reset_index(), "g3_matriz_comparativa")
matriz.T
'''),
    code('''
fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
indicadores = [("importaciones_totales_2025_kusd", "Tamaño del mercado", "USD importados"),
               ("crec_importaciones_5a_pct", "Crecimiento de las importaciones", "% en 5 años"),
               ("cuota_colombia_pct", "Cuota de Colombia", "% de sus importaciones")]
for ax, (col, titulo, unidad) in zip(axes, indicadores):
    valores = matriz[col]
    ax.bar(valores.index, valores, color=CATEGORIAS[:3], width=0.55)
    for x, v in enumerate(valores):
        ax.annotate(fmt_miles(v) if "kusd" in col else f"{v:.1f}", (x, v), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9, color=GRIS_TEXT)
    if "kusd" in col:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_miles))
    estilo(ax, titulo, unidad, eje_y=unidad)
axes[2].figure.text(0.01, -0.03, "Fuente: Trade Map (ITC), 2025.", fontsize=8, color=GRIS_EJE)
plt.tight_layout()
guardar(fig, "g3_matriz_comparativa")
'''),
    analisis(),

    md("---\n# 7. Escenarios de diversificación\n\nLa ficha propone tomar la participación actual de cada mercado, aplicarle una tasa de crecimiento durante dos años y **mantener fijas las exportaciones totales**: lo que ganan los tres candidatos lo pierde Estados Unidos. Los tres escenarios y sus tasas son **editables**."),
    code('''
# ====================== EDITABLE: escenarios (crecimiento anual, %) ======================
ESCENARIOS = {
    "Actual":            {"Alemania": 0,  "Japón": 0, "Corea del Sur": 0},
    "Conservador":       {"Alemania": 10, "Japón": 3, "Corea del Sur": 10},
    "Alineado con 2025": {"Alemania": 30, "Japón": 8, "Corea del Sur": 43},
}
ANIOS_PROYECCION = 2
# ==========================================================================================

def proyectar(participaciones, crecimientos, anios, absorbe=EEUU):
    """Aplica crecimiento a los mercados indicados manteniendo el total en 100 %; el mercado `absorbe` recibe el residuo."""
    nuevas = participaciones.copy()
    for mercado, tasa in crecimientos.items():
        etiqueta = CANDIDATOS[mercado]
        nuevas[etiqueta] = participaciones[etiqueta] * (1 + tasa / 100) ** anios
    ganancia = nuevas.sum() - participaciones.sum()
    nuevas[absorbe] = participaciones[absorbe] - ganancia
    return nuevas

participacion_2025 = destinos_2025.set_index("pais")["participacion_pct"]
resultado = pd.DataFrame({nombre: proyectar(participacion_2025, tasas, ANIOS_PROYECCION) for nombre, tasas in ESCENARIOS.items()})
resultado = resultado.loc[FOCO]
resultado.loc["Otros"] = 100 - resultado.sum()
exportar(resultado.reset_index(), "g3_escenarios")
resultado.round(2)
'''),
    code('''
fig, ax = plt.subplots(figsize=(10, 5))
mercados = resultado.index.tolist()
x = np.arange(len(mercados))
ancho_barra = 0.26
for i, (escenario, color) in enumerate(zip(resultado.columns, CATEGORIAS)):
    barras = ax.bar(x + (i - 1) * ancho_barra, resultado[escenario], width=ancho_barra, color=color, label=escenario)
    for b in barras:
        ax.annotate(f"{b.get_height():.1f}", (b.get_x() + b.get_width() / 2, b.get_height()), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8, color=GRIS_TEXT)
ax.set_xticks(x)
ax.set_xticklabels([m.replace(", República de", "") for m in mercados])
ax.legend(frameon=False, fontsize=9)
estilo(ax, f"Participación de cada destino tras {ANIOS_PROYECCION} años, por escenario", "% de las exportaciones colombianas de café verde; el total se mantiene fijo",
       "Elaboración del equipo con Trade Map (ITC), 2025.", eje_y="%")
guardar(fig, "g3_escenarios")
'''),
    analisis("¿Qué supuesto es más frágil: las tasas de crecimiento o el total fijo? ¿Qué participación de Estados Unidos consideran aceptable?"),

    cierre([REF_BAENA]),
]

escribir(celdas, NB)
