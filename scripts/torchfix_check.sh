#!/usr/bin/env bash
# TorchFix esce sempre con codice 0, anche quando trova problemi.
# Questo wrapper converte i risultati in annotazioni GitHub e fa fallire il job se ce ne sono.
set -uo pipefail
TARGET="${1:-.}"
out=$(torchfix "$TARGET" 2>&1 | grep -E ':[0-9]+:[0-9]+: TOR[0-9]+' || true)
if [ -z "$out" ]; then
  echo "TorchFix: nessun problema trovato"
  exit 0
fi
echo "$out" | sed -E 's/^([^:]+):([0-9]+):([0-9]+): (.*)$/::warning file=\1,line=\2,col=\3::\4/'
echo "TorchFix: trovati $(echo "$out" | wc -l) problemi"
exit 1
