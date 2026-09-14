#!/bin/zsh
# Regenera los siete cuadernos y, con --verificar, los ejecuta en modo local.
cd "$(dirname "$0")"
for g in 1 2 3 4 5 6 7; do python3 grupo$g.py || exit 1; done
if [[ "$1" == "--verificar" ]]; then
  ./ejecutar.sh "../Grupo 1/Grupo_1_Uchuva.ipynb"
  ./ejecutar.sh "../Grupo 2/Grupo_2_Cacao.ipynb"
  ./ejecutar.sh "../Grupo 3/Grupo_3_Cafe.ipynb"
  ./ejecutar.sh "../Grupo 4/Grupo_4_Esmeraldas.ipynb"
  ./ejecutar.sh "../Grupo 5/Grupo_5_Cacao_EUDR.ipynb"
  ./ejecutar.sh "../Grupo 6/Grupo_6_Curuba.ipynb"
  ./ejecutar.sh "../Grupo 7/Grupo_7_Rosas.ipynb"
fi
