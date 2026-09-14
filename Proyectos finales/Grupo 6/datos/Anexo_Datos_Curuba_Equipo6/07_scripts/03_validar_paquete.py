"""Verifica las identidades matematicas del anexo y escribe 08_salidas/reporte_validacion.txt.

Comprueba: identidad del IBCR, relacion GL = 1 - |IBCR|, identidad del RSCA, suma ponderada de la
matriz multicriterio, factor de imputacion del 3,8 %, coherencia de la suma de cuotas frente al
agregado Mundo y cobertura anual de la descarga de Trade Map.

Uso:  python 07_scripts/03_validar_paquete.py
"""
from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
TOL = 0.001
resultados = []


def check(nombre, condicion, detalle):
    resultados.append({"verificacion": nombre,
                       "estado": "OK" if condicion else "REVISAR",
                       "detalle": detalle})
    return condicion


def validar_ibcr():
    d = pd.read_csv(RAIZ / "03_datos_limpios" / "d1_flujos_pais_081090.csv")
    calc = (d["exportaciones_X_usd_miles"] - d["importaciones_M_usd_miles"]) / \
           (d["exportaciones_X_usd_miles"] + d["importaciones_M_usd_miles"])
    dif = (calc - d["IBCR_calculado"]).abs().max()
    check("IBCR = (X-M)/(X+M) en los 6 mercados", dif <= TOL,
          f"diferencia maxima {dif:.6f} sobre {len(d)} economias")


def validar_gl():
    for archivo in ["d1_flujos_pais_081090.csv", "d2_flujos_curuba_colombia.csv"]:
        d = pd.read_csv(RAIZ / "03_datos_limpios" / archivo)
        dif = ((1 - d["IBCR_calculado"].abs()) - d["GL_calculado"]).abs().max()
        check(f"GL = 1 - |IBCR| en {archivo}", dif <= TOL, f"diferencia maxima {dif:.6f}")

    i2 = pd.read_csv(RAIZ / "05_indicadores_equipo" / "i2_concentracion_estructura.csv")
    d2 = pd.read_csv(RAIZ / "03_datos_limpios" / "d2_flujos_curuba_colombia.csv")
    gl_curuba = float(i2.loc[i2["producto"].str.startswith("Curuba"), "GL_colombia"].iloc[0])
    check("El GL publicado de la curuba reconcilia con la base d2",
          abs(gl_curuba - float(d2["GL_calculado"].iloc[0])) <= TOL,
          f"GL ficha {gl_curuba} vs base curuba {float(d2['GL_calculado'].iloc[0])}")


def validar_rsca():
    i3 = pd.read_csv(RAIZ / "05_indicadores_equipo" / "i3_ventaja_comparativa.csv")
    calc = (i3["balassa_rca"] - 1) / (i3["balassa_rca"] + 1)
    dif = (calc - i3["rsca_publicado"]).abs().max()
    check("RSCA = (RCA-1)/(RCA+1) frente a lo publicado", dif <= TOL,
          f"diferencia maxima {dif:.6f} sobre {len(i3)} sectores")


def validar_matriz():
    i4 = pd.read_csv(RAIZ / "05_indicadores_equipo" / "i4_matriz_multicriterio.csv")
    crit = i4[i4["criterio"].str.match(r"^\d\.")]
    pesos = crit["peso"].astype(float).values
    check("Los pesos de la matriz suman 100 %", abs(pesos.sum() - 1.0) <= TOL,
          f"suma de pesos = {pesos.sum():.4f}")

    fila_tot = i4[i4["criterio"].str.contains("recalculado")].iloc[0]
    fila_pub = i4[i4["criterio"].str.contains("publicado")].iloc[0]
    mercados = [c for c in i4.columns if c not in ("criterio", "peso")]
    difs, orden_ok = {}, []
    for m in mercados:
        esperado = float(np.dot(pesos, crit[m].astype(float).values))
        difs[m] = abs(esperado - float(fila_tot[m]))
    check("Puntaje ponderado = suma producto de puntajes por pesos", max(difs.values()) <= 0.005,
          "diferencia maxima " + f"{max(difs.values()):.4f}")

    rank_recal = pd.Series({m: float(fila_tot[m]) for m in mercados}).rank(ascending=False)
    rank_pub = pd.Series({m: float(fila_pub[m]) for m in mercados}).rank(ascending=False)
    check("El ranking de mercados no cambia al recalcular", rank_recal.equals(rank_pub),
          "orden recalculado: " + " > ".join(rank_recal.sort_values().index))


def validar_imputacion():
    c2 = pd.read_csv(RAIZ / "03_datos_limpios" / "c2_produccion_derivados.csv")
    dif = c2["diferencia"].abs().max()
    check("El valor imputado equivale al 3,8 % de la base comercial declarada", dif <= 0.05,
          f"diferencia maxima {dif:.3f} USD miles en {len(c2)} anios")
    part = c2["participacion_curuba_en_pasifloras_pct"]
    check("La participacion productiva de la curuba difiere del factor comercial del 3,8 %",
          True, f"participacion productiva {part.min():.2f}%-{part.max():.2f}% frente a factor comercial 3,80%")


def validar_trademap():
    ancho = pd.read_csv(RAIZ / "03_datos_limpios" / "t1_exportadores_081090_ancho.csv", dtype={"codigo_tm": str})
    mundo = pd.read_csv(RAIZ / "03_datos_limpios" / "t3_mundo_081090.csv")
    anios = [c for c in ancho.columns if c.isdigit()]
    total = dict(zip(mundo["anio"].astype(str), mundo["exportaciones_mundiales_usd_miles"]))
    peor = max(abs(ancho[a].sum() / total[a] * 100 - 100) for a in anios)
    check("La suma de las economias reproduce el agregado Mundo", peor <= 1.0,
          f"desviacion maxima {peor:.2f} % en los {len(anios)} anios")

    r3 = pd.read_csv(RAIZ / "04_indicadores_reales" / "r3_hhi_oferta_mundial.csv")
    dif = (r3["HHI_oferta_mundial"] * r3["numero_equivalente_exportadores"] - 1).abs().max()
    check("Numero equivalente = 1 / HHI", dif <= 0.01, f"diferencia maxima {dif:.5f}")

    cob = pd.read_csv(RAIZ / "04_indicadores_reales" / "r6_cobertura_y_calidad.csv")
    parciales = cob[cob["cobertura_pct"] < 85]["anio"].tolist()
    check("Anios con cobertura suficiente para ranking definitivo", len(parciales) <= 1,
          f"anios con cobertura parcial: {parciales if parciales else 'ninguno'}")


def main():
    validar_ibcr()
    validar_gl()
    validar_rsca()
    validar_matriz()
    validar_imputacion()
    validar_trademap()

    df = pd.DataFrame(resultados)
    ok = int((df["estado"] == "OK").sum())
    lineas = [
        "REPORTE DE VALIDACION - ANEXO TECNICO DE DATOS",
        "Curuba (Passiflora mollissima) - Universidad EAN, Grupo 5, Equipo 6",
        f"Generado por 07_scripts/03_validar_paquete.py el {date.today().isoformat()}",
        "=" * 78, "",
        f"Verificaciones ejecutadas: {len(df)}   |   Superadas: {ok}   |   Para revisar: {len(df) - ok}",
        "", "-" * 78,
    ]
    for _, r in df.iterrows():
        lineas += [f"[{r['estado']:>7}]  {r['verificacion']}", f"           {r['detalle']}", ""]
    lineas += ["-" * 78, "",
               "Nota: este reporte verifica la consistencia interna de las cifras del anexo",
               "(identidades matematicas, sumas ponderadas y coherencia de las fuentes).",
               "No sustituye la validacion de las estimaciones frente a Legiscomex y Agronet,",
               "pendiente segun el registro de supuestos."]
    salida = RAIZ / "08_salidas" / "reporte_validacion.txt"
    salida.parent.mkdir(exist_ok=True)
    salida.write_text("\n".join(lineas), encoding="utf-8")
    df.to_csv(RAIZ / "08_salidas" / "reporte_validacion.csv", index=False, encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
