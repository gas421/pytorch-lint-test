#!/usr/bin/env python3
"""Filtra i risultati di un linter alle sole righe aggiunte o modificate nella PR.

Legge da stdin righe nel formato  path:riga:colonna: messaggio
(prodotto da `ruff check --output-format=concise` e da `torchfix`),
tiene solo quelle su righe cambiate rispetto a --base, e le stampa come
annotazioni GitHub (::error o ::warning). Esce con 1 se ne resta almeno una.

Senza --base (es. push su main) non filtra: riporta tutto.

Uso:
  ruff check --output-format=concise --exit-zero FILE... \
    | python scripts/diff_filter.py --base origin/main
  torchfix FILE... | python scripts/diff_filter.py --base origin/main --level warning
"""

import argparse
import re
import subprocess
import sys

FINDING = re.compile(r"^(?P<path>[^:\s]+\.py):(?P<line>\d+):(?P<col>\d+): (?P<msg>.+)$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@")


def changed_lines(base: str) -> dict[str, set[int]]:
    """Mappa file -> numeri di riga aggiunti o modificati nella PR."""
    diff = subprocess.run(
        ["git", "diff", "--unified=0", "--diff-filter=ACMR", base, "HEAD", "--", "*.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    result: dict[str, set[int]] = {}
    current = None
    for row in diff.splitlines():
        if row.startswith("+++ b/"):
            current = row[len("+++ b/") :]
            result.setdefault(current, set())
        elif current and (m := HUNK.match(row)):
            start = int(m["start"])
            count = int(m["count"]) if m["count"] is not None else 1
            result[current].update(range(start, start + count))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="", help="ref di confronto, es. origin/main")
    parser.add_argument("--level", choices=["error", "warning"], default="error")
    args = parser.parse_args()

    lines = changed_lines(args.base) if args.base else None
    kept = skipped = 0
    for raw in sys.stdin:
        m = FINDING.match(raw.strip())
        if not m:
            continue
        path, line = m["path"].removeprefix("./"), int(m["line"])
        if lines is not None and line not in lines.get(path, set()):
            skipped += 1
            continue
        kept += 1
        print(f"::{args.level} file={path},line={line},col={m['col']}::{m['msg']}")

    scope = "righe modificate nella PR" if lines is not None else "tutto il codice"
    print(f"Problemi su {scope}: {kept} (ignorati su righe non toccate: {skipped})")
    return 1 if kept else 0


if __name__ == "__main__":
    sys.exit(main())
