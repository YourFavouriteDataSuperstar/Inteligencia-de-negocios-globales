"""Calcula los indicadores reales sobre la descarga de Trade Map y escribe 04_indicadores_reales/.

Indicadores: participacion de mercado, ranking, HHI de la oferta mundial, numero equivalente,
CAGR y cobertura anual de la fuente.

Uso:  python 07_scripts/02_calcular_indicadores.py
"""
from pathlib import Path
import pandas as pd
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
LIMPIOS = RAIZ / "03_datos_limpios"
SALIDA = RAIZ / "04_indicadores_reales"
FOCO = ["Colombia", "Ecuador", "Perú", "Países Bajos", "Tailandia", "China", "España",
        "Türkiye", "Egipto", "India"]


def hhi(valores):
    """Indice de Herfindahl-Hirschman sobre un vector de valores absolutos (escala 0-1)."""
    v = pd.Series(valores).dropna()
    cuotas = v / v.sum()
    return float((cuotas ** 2).sum())


def cagr(inicial, final, anios):
    """Tasa de crecimiento anual compuesta, en porcentaje."""
    if not inicial or not final or inicial <= 0:
        return np.nan
    return ((final / inicial) ** (1 / anios) - 1) * 100


def main():
    ancho = pd.read_csv(LIMPIOS / "t1_exportadores_081090_ancho.csv", dtype={"codigo_tm": str})
    mundo = pd.read_csv(LIMPIOS / "t3_mundo_081090.csv")
    anios = [c for c in ancho.columns if c.isdigit()]
    total = dict(zip(mundo["anio"].astype(str), mundo["exportaciones_mundiales_usd_miles"]))

    # Participacion de mercado
    cuotas = ancho.copy()
    for a in anios:
        cuotas[a] = (ancho[a] / total[a] * 100).round(3)
    cuotas.head(25).to_csv(SALIDA / "r1_participacion_mercado_top25_pct.csv", index=False, encoding="utf-8")

    # Concentracion de la oferta mundial
    filas = []
    for a in anios:
        v = ancho[a].dropna()
        h = hhi(v)
        filas.append({"anio": int(a), "economias_con_dato": int(v.notna().sum()),
                      "exportaciones_mundiales_usd_miles": total[a],
                      "HHI_oferta_mundial": round(h, 4), "HHI_escala_10000": round(h * 10000, 1),
                      "numero_equivalente_exportadores": round(1 / h, 2),
                      "cuota_mayor_exportador_pct": round(float(v.max() / v.sum() * 100), 2),
                      "cuota_top5_pct": round(float(v.nlargest(5).sum() / v.sum() * 100), 2)})
    pd.DataFrame(filas).to_csv(SALIDA / "r3_hhi_oferta_mundial.csv", index=False, encoding="utf-8")

    # Ranking mundial por anio de las economias de interes
    rank = pd.DataFrame({"anio": [int(a) for a in anios]})
    for p in FOCO[:7]:
        f = ancho[ancho["pais"] == p]
        if f.empty:
            continue
        f = f.iloc[0]
        rank[f"puesto_{p}"] = [int((ancho[a] > f[a]).sum()) + 1 if pd.notna(f[a]) else np.nan for a in anios]
    rank.to_csv(SALIDA / "r2_ranking_exportadores.csv", index=False, encoding="utf-8")

    # Crecimiento y cuota de las economias de interes
    n = len(anios) - 1
    reg = []
    for p in FOCO:
        f = ancho[ancho["pais"] == p]
        if f.empty:
            continue
        f = f.iloc[0]
        reg.append({"pais": p,
                    f"exportaciones_{anios[0]}_usd_miles": f[anios[0]],
                    f"exportaciones_{anios[-2]}_usd_miles": f[anios[-2]],
                    f"exportaciones_{anios[-1]}_usd_miles": f[anios[-1]],
                    f"cagr_{anios[0]}_{anios[-1]}_pct": round(cagr(f[anios[0]], f[anios[-1]], n), 2),
                    f"cagr_{anios[0]}_{anios[-2]}_pct": round(cagr(f[anios[0]], f[anios[-2]], n - 1), 2),
                    f"variacion_total_{anios[0]}_{anios[-1]}_pct": round((f[anios[-1]] / f[anios[0]] - 1) * 100, 1),
                    "cuota_final_pct": round(f[anios[-1]] / total[anios[-1]] * 100, 2),
                    "puesto_final": int((ancho[anios[-1]] > f[anios[-1]]).sum()) + 1})
    pd.DataFrame(reg).to_csv(SALIDA / "r4_crecimiento_y_cuota.csv", index=False, encoding="utf-8")

    # Colombia frente a sus competidores andinos
    andinos = ancho[ancho["pais"].isin(["Colombia", "Ecuador", "Perú"])].set_index("pais")
    comp = pd.DataFrame({"anio": [int(a) for a in anios]})
    for p in ["Colombia", "Ecuador", "Perú"]:
        comp[f"{p}_usd_miles"] = [andinos.loc[p, a] for a in anios]
        comp[f"{p}_cuota_pct"] = [round(andinos.loc[p, a] / total[a] * 100, 2) for a in anios]
    comp["razon_ecuador_colombia"] = (comp["Ecuador_usd_miles"] / comp["Colombia_usd_miles"]).round(2)
    comp["razon_peru_colombia"] = (comp["Perú_usd_miles"] / comp["Colombia_usd_miles"]).round(2)
    comp.to_csv(SALIDA / "r5_colombia_vs_competidores_andinos.csv", index=False, encoding="utf-8")

    # Cobertura de la fuente
    cob = pd.DataFrame({"anio": [int(a) for a in anios],
                        "economias_reportadas": [int(ancho[a].notna().sum()) for a in anios],
                        "economias_sin_dato": [int(ancho[a].isna().sum()) for a in anios],
                        "cobertura_pct": [round(ancho[a].notna().sum() / len(ancho) * 100, 1) for a in anios]})
    cob["apto_para_ranking_completo"] = np.where(cob["cobertura_pct"] >= 85, "Si", "No - cobertura parcial")
    cob.to_csv(SALIDA / "r6_cobertura_y_calidad.csv", index=False, encoding="utf-8")
    print("Indicadores recalculados en 04_indicadores_reales/")


if __name__ == "__main__":
    main()
