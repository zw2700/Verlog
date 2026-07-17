#!/usr/bin/env bash
# Runs the env driver in each repo via a fresh subprocess (isolation avoids the
# verl.* module-name collision) and diffs the reward-trajectory JSON.
set -u
PY=/zfsauton/scratch/cpulling/conda_envs/qwen35/bin/python
[ -x "$PY" ] || PY=/zfsauton/scratch/cpulling/conda_envs/verlog/bin/python
DRIVER=/tmp/claude-1376/-zfsauton-scratch-cpulling/7131f858-ae32-44a1-9a70-b26664de3a48/scratchpad/env_parity_driver.py
ORIG=/zfsauton/scratch/cpulling/Verlog
PORT=/zfsauton2/home/cpulling/Verlog_v08
OUT=/tmp/claude-1376/-zfsauton-scratch-cpulling/7131f858-ae32-44a1-9a70-b26664de3a48/scratchpad
extract() { sed -n '/PARITY_JSON_BEGIN/,/PARITY_JSON_END/p' "$1" | grep -vE "PARITY_JSON_(BEGIN|END)"; }

STATUS=0
for MODE in individual group combined; do
  echo "========== reward_mode=$MODE =========="
  "$PY" "$DRIVER" "$ORIG" "$MODE" > "$OUT/orig_$MODE.log" 2>"$OUT/orig_$MODE.err"
  rc1=$?
  "$PY" "$DRIVER" "$PORT" "$MODE" > "$OUT/port_$MODE.log" 2>"$OUT/port_$MODE.err"
  rc2=$?
  if [ $rc1 -ne 0 ] || [ $rc2 -ne 0 ]; then
    echo "  DRIVER ERROR (orig rc=$rc1, port rc=$rc2)"; echo "  --- orig err ---"; tail -5 "$OUT/orig_$MODE.err"; echo "  --- port err ---"; tail -5 "$OUT/port_$MODE.err"; STATUS=1; continue
  fi
  extract "$OUT/orig_$MODE.log" > "$OUT/orig_$MODE.json"
  extract "$OUT/port_$MODE.log" > "$OUT/port_$MODE.json"
  if diff -q "$OUT/orig_$MODE.json" "$OUT/port_$MODE.json" >/dev/null; then
    consensus=$("$PY" -c "import json;d=json.load(open('$OUT/port_$MODE.json'));print('consensus=%s choice=%s steps=%d'%(d['consensus_reached'],d['consensus_choice'],len(d['trajectory'])))")
    echo "  REWARD TRAJECTORY IDENTICAL  ($consensus)"
  else
    echo "  *** MISMATCH ***"; diff "$OUT/orig_$MODE.json" "$OUT/port_$MODE.json" | head -20; STATUS=1
  fi
done
echo "======================================="
[ $STATUS -eq 0 ] && echo "ALL REWARD MODES: original == port (cap=None)" || echo "PARITY FAILURE — see above"
exit $STATUS
