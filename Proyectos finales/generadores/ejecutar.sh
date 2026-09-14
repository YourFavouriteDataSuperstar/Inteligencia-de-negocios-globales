#!/bin/zsh
# Ejecuta un cuaderno en MODO local desde su carpeta (verificacion de punta a punta).
# Uso: ./ejecutar.sh "../Grupo 7/Grupo_7_Rosas.ipynb"
# El cuaderno ejecutado (con salidas) queda en generadores/ejecutados/, carpeta ignorada por git.
NB="$1"; DIR=$(dirname "$NB"); NOMBRE=$(basename "$NB" .ipynb)
OUT="$(cd "$(dirname "$0")" && pwd)/ejecutados"
mkdir -p "$OUT"
cd "$DIR" && MPLBACKEND=Agg python3 - "$NOMBRE" "$OUT" <<'PY'
import sys, os, nbformat
from nbclient import NotebookClient
nombre, out = sys.argv[1], sys.argv[2]
nb = nbformat.read(nombre + ".ipynb", as_version=4)
for c in nb.cells:
    if c.cell_type == "code" and 'MODO = "github"' in c.source:
        c.source = c.source.replace('MODO = "github"', 'MODO = "local"')
client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": "."}})
try:
    client.execute(); print("OK:", nombre)
except Exception as e:
    print("ERROR en", nombre); print(str(e)[-3000:]); sys.exit(1)
finally:
    nbformat.write(nb, os.path.join(out, nombre + "_ejecutado.ipynb"))
PY
