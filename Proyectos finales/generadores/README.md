# Generadores de los cuadernos de proyectos finales

Los cuadernos `Grupo_N_*.ipynb` no se editan a mano: se generan con estos scripts.
Así los siete comparten las mismas celdas de configuración, descarga, lectores y fórmulas.

| Archivo | Qué hace |
|---|---|
| `comun.py` | Piezas compartidas: portada, celda de imports y paleta, configuración, descarga desde GitHub, lectores de Trade Map / Banco Mundial / canasta HS2, fórmulas de los cuadernos 2-4, cierre |
| `grupo1.py` … `grupo7.py` | Las celdas específicas de cada grupo (una sección por métrica de su ficha técnica) |
| `generar_todos.sh` | Regenera los siete cuadernos; con `--verificar` además los ejecuta en modo local |
| `ejecutar.sh` | Ejecuta un cuaderno en modo local desde su carpeta y guarda la copia con salidas en `ejecutados/` |
| `descargar_trademap.sh` | Cómo se bajaron los CSV de Trade Map (API pública de la versión beta) para los grupos 1-4 |

## Uso

```bash
cd "Proyectos finales/generadores"
./generar_todos.sh --verificar      # regenera y ejecuta los siete cuadernos
python3 grupo7.py                   # solo uno
```

Requisitos locales: Python 3.9+, `pandas`, `numpy`, `matplotlib`, `openpyxl`, `lxml`, `nbformat`, `nbclient`.

Para cambiar algo en todos los cuadernos (por ejemplo, la paleta o un lector), edita `comun.py` y regenera.
Para cambiar el análisis de un grupo, edita su `grupoN.py`. Los cuadernos se escriben sin salidas guardadas.

El archivo `faostat_cacao_2015_2024.csv` del grupo 2 se extrajo de los archivos masivos regionales de FAOSTAT
(`Production_Crops_Livestock_E_Americas.zip` y `_Africa.zip`), filtrando cacao en grano (código 661) para
Colombia, Ecuador, Perú, Ghana y Côte d'Ivoire.
