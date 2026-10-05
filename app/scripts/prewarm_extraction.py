"""Pre-legge i documenti della demo e ne salva l'estrazione nella cache.

L'estrazione reale richiede 40-100 s per documento (QA-24): lanciando
questo script prima del pitch, in demo il caricamento degli stessi file
riusa il risultato salvato ed e' immediato (nessun costo, stesso output).

Uso, dalla root del repo:
    .venv/Scripts/python app/scripts/prewarm_extraction.py app/demo_assets/*.pdf app/demo_assets/*.xlsx
"""
from __future__ import annotations

import glob
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finsup.extraction import extract_budget_items, save_upload  # noqa: E402


def main(patterns: list[str]) -> int:
    # PowerShell non espande i * per i programmi esterni: lo facciamo qui.
    files = [f for p in patterns for f in (glob.glob(p) or [p])]
    # Stesso percorso dell'app: copia in UPLOAD_DIR, poi estrazione.
    paths = [save_upload(Path(f).name, Path(f).read_bytes()) for f in files]
    with ThreadPoolExecutor(max_workers=max(len(paths), 1)) as pool:
        results = list(pool.map(extract_budget_items, paths))
    failed = 0
    for path, r in zip(paths, results):
        if r["error"]:
            failed += 1
            print(f"ERRORE  {path.name}: {r['error']}")
        else:
            origin = "gia' in cache" if r["cached"] else f"letto ora, ${r['cost_usd']:.3f}"
            print(f"ok      {path.name}: {len(r['incomes'])} entrate, {len(r['expenses'])} uscite ({origin})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
