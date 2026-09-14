"""Limpia la descarga cruda de Trade Map y escribe las tablas de 03_datos_limpios/.

Uso:  python 07_scripts/01_preparar_datos.py
"""
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CRUDO = RAIZ / "02_datos_crudos" / "exporting-economies_081090.xlsx"
SALIDA = RAIZ / "03_datos_limpios"
CODIGO_MUNDO = "000"


def cargar_crudo(ruta=CRUDO):
    """Lee el XLSX de Trade Map conservando los ceros a la izquierda de los codigos."""
    return pd.read_excel(ruta, sheet_name="Data",
                         dtype={"reporterCd": str, "partnerCd": str, "productCd": str})


def limpiar(df):
    """Separa el agregado mundial, retira columnas constantes y normaliza nombres de columna."""
    anios = [c for c in df.columns if "USD" in c]
    mundo = df[df["reporterCd"] == CODIGO_MUNDO]
    paises = df[df["reporterCd"] != CODIGO_MUNDO]

    ancho = paises[["reporterCd", "reporterLabel"] + anios].copy()
    ancho.columns = ["codigo_tm", "pais"] + [c[:4] for c in anios]
    ancho = ancho.sort_values(ancho.columns[-1], ascending=False, na_position="last").reset_index(drop=True)

    largo = ancho.melt(id_vars=["codigo_tm", "pais"], var_name="anio",
                       value_name="exportaciones_usd_miles")
    largo["anio"] = largo["anio"].astype(int)
    largo = largo.dropna(subset=["exportaciones_usd_miles"])

    serie_mundo = pd.DataFrame({"anio": [int(c[:4]) for c in anios],
                                "exportaciones_mundiales_usd_miles": [float(mundo[c].iloc[0]) for c in anios]})
    return ancho, largo, serie_mundo


def main():
    ancho, largo, mundo = limpiar(cargar_crudo())
    SALIDA.mkdir(exist_ok=True)
    ancho.to_csv(SALIDA / "t1_exportadores_081090_ancho.csv", index=False, encoding="utf-8")
    largo.sort_values(["anio", "exportaciones_usd_miles"], ascending=[True, False]).to_csv(
        SALIDA / "t2_exportadores_081090_largo.csv", index=False, encoding="utf-8")
    mundo.to_csv(SALIDA / "t3_mundo_081090.csv", index=False, encoding="utf-8")
    print(f"Economias: {len(ancho)} | Anios: {len(mundo)} | Filas formato largo: {len(largo)}")


if __name__ == "__main__":
    main()
