#!/bin/zsh
# Descarga tablas de Trade Map (beta) por API publica. Etiquetas en espanol.
set -e
BASE="https://www.trademap.org/api/goods"
H=(-H "User-Agent: Mozilla/5.0" -H "Accept-Language: es")
IND_P="VAL,BAL,QTY,UV,S,SPC,SPW,RKP,GV5,GV2,GV5P,GQ5"
IND_C="VAL,BAL,QTY,UV,SW,GV5,GV2,GQ5"

ts() { # flow country product destino
  curl -sS "${H[@]}" -o "$4" "$BASE/timeSeries/yearly/byPartner?tradeFlow=$1&product=$3&country=$2&partner=000&periodFrom=2016&periodTo=2025&directMirror=D&indicator=VAL&page=1&pageSize=1000&sortBy=2025&sortDir=desc&currency=USD&export=csv"
  echo "$(wc -l < "$4") lineas -> $4"; }
ind_partner() { # flow country product destino
  curl -sS "${H[@]}" -o "$4" "$BASE/tradeIndicators/byPartner?tradeFlow=$1&product=$3&country=$2&partner=000&directMirror=D&indicators=$IND_P&page=1&pageSize=1000&sortBy=VAL&sortDir=desc&export=csv"
  echo "$(wc -l < "$4") lineas -> $4"; }
ind_country() { # flow product destino
  curl -sS "${H[@]}" -o "$3" "$BASE/tradeIndicators/byCountry?tradeFlow=$1&product=$2&country=000&partner=000&directMirror=D&indicators=$IND_C&page=1&pageSize=1000&sortBy=VAL&sortDir=desc&export=csv"
  echo "$(wc -l < "$3") lineas -> $3"; }

cd "$(dirname "$0")/../.."      # raiz del repositorio
G="Proyectos finales"
mkdir -p "$G/Grupo 2/datos" "$G/Grupo 3/datos"

# Grupo 2 - cacao 1801
ts E 170 1801 "$G/Grupo 2/datos/colombias-exports-to-world-by-importer_1801.csv"
ind_partner E 170 1801 "$G/Grupo 2/datos/colombias-exports-to-world-in-2025-by-importer_1801.csv"
ind_partner I 170 1801 "$G/Grupo 2/datos/colombias-imports-from-world-in-2025-by-exporter_1801.csv"
ind_country E 1801 "$G/Grupo 2/datos/exporting-countries-in-2025_1801.csv"
ind_country I 1801 "$G/Grupo 2/datos/importing-countries-in-2025_1801.csv"

# Grupo 3 - cafe 090111
ts E 170 090111 "$G/Grupo 3/datos/colombias-exports-to-world-by-importer_090111.csv"
ind_partner E 170 090111 "$G/Grupo 3/datos/colombias-exports-to-world-in-2025-by-importer_090111.csv"
ind_country I 090111 "$G/Grupo 3/datos/importing-countries-in-2025_090111.csv"
ind_country E 090111 "$G/Grupo 3/datos/exporting-countries-in-2025_090111.csv"
ind_partner I 276 090111 "$G/Grupo 3/datos/germanys-imports-from-world-in-2025-by-exporter_090111.csv"
ind_partner I 392 090111 "$G/Grupo 3/datos/japans-imports-from-world-in-2025-by-exporter_090111.csv"
ind_partner I 410 090111 "$G/Grupo 3/datos/koreas-imports-from-world-in-2025-by-exporter_090111.csv"

# Series adicionales para grupos 1 y 4
ts E 170 081090 "$G/Grupo 1/datos/colombias-exports-to-world-by-importer_081090.csv"
ts E 170 710391 "$G/Grupo 4/datos/colombias-exports-to-world-by-importer_710391.csv"
