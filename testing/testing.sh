#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
cd ${SCRIPT_DIR};

python3 ../bin/monitor.py -id ../testing/updates/tests -jo ../testing/results/default.json;
python3 ../bin/monitor.py -id ../testing/updates/tests -jo ../testing/results/country.json -cf LU;
python3 ../bin/monitor.py -id ../testing/updates/tests -jo ../testing/results/asn.json -af 268696 3356;
python3 ../bin/monitor.py -id ../testing/updates/tests -jo ../testing/results/asn_neg.json -af _3356 _17794 _265636;
python3 ../bin/monitor.py -id ../testing/updates/tests -jo ../testing/results/prefix_exact.json -pf 38.126.253.0/24 59.90.188.0/24 --match exact;
python3 ../bin/monitor.py -id ../testing/updates/tests -jo ../testing/results/prefix_more.json -pf 38.126.0.0/16;
python3 ../bin/monitor.py -id ../testing/updates/tests -jo ../testing/results/ipversion.json --ipversion 4;
