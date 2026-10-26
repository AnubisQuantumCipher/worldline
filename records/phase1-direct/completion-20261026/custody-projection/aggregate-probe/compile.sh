#!/bin/bash
set -e
source /home/sicarii/opt/gnat/env.sh
cd /home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/completion-20261026/custody-projection/aggregate-probe
exec gcc -S -gnat2022 -gnatwa -gnatVa -gnatf -O2 -g -fPIC -fno-var-tracking-assignments -gnata -fstack-usage -fdump-tree-original -fdump-tree-optimized -I/home/sicarii/Work/worldline-phase1-direct-20261019/core -I/home/sicarii/Work/worldline-phase1-direct-20261019/core/attest projection_aggregate_probe.adb -o projection_aggregate_probe.s
