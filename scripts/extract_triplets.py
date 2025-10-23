#!/usr/bin/env python3
import argparse, csv, os, re, sys
from typing import Iterable, Set, Tuple

TRIPLET_RE = re.compile(
    r"<IdAplicacion>\s*([^<]+?)\s*</IdAplicacion>\s*"
    r"<IdServicio>\s*([^<]+?)\s*</IdServicio>\s*"
    r"<IdTransaccion>\s*([^<]+?)\s*</IdTransaccion>",
    re.DOTALL | re.IGNORECASE,  # tolera saltos y mayúsc/minúsc
)

def read_text_best_effort(path: str) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def iter_files(directory: str) -> Iterable[str]:
    with os.scandir(directory) as it:
        for e in it:
            if e.is_file():
                yield e.path

def extract_triplets_from_text(text: str) -> Iterable[Tuple[str, str, str]]:
    for a, s, t in TRIPLET_RE.findall(text):
        yield (a.strip(), s.strip(), t.strip())

def main() -> None:
    p = argparse.ArgumentParser(
        description="Extract unique IdAplicacion,IdServicio,IdTransaccion from logs into CSV (non-recursive)."
    )
    p.add_argument("--root", required=True, help="Directory with logs (non-recursive).")
    p.add_argument("--output", required=True, help="CSV output path.")
    p.add_argument("--no-sort", action="store_true", help="Do not sort output.")
    p.add_argument("--verbose", action="store_true", help="Show per-file progress.")
    args = p.parse_args()

    root = os.path.abspath(args.root)
    out = os.path.abspath(args.output)

    if not os.path.isdir(root):
        print(f"[error] Directory not found: {root}", flush=True)
        sys.exit(2)

    files = list(iter_files(root))
    if args.verbose:
        print(f"[info] Folder: {root}", flush=True)
        print(f"[info] Files found: {len(files)}", flush=True)
        print(f"[info] Output CSV: {out}", flush=True)

    if not files:
        print("[warn] No files to scan in the provided folder.", flush=True)
        sys.exit(0)

    unique: Set[Tuple[str, str, str]] = set()
    for path in files:
        try:
            text = read_text_best_effort(path)
        except Exception as ex:
            if args.verbose:
                print(f"[warn] Skipping {os.path.basename(path)}: {ex}", flush=True)
            continue

        before = len(unique)
        for triplet in extract_triplets_from_text(text):
            unique.add(triplet)
        added = len(unique) - before
        if args.verbose:
            print(f"[ok] {os.path.basename(path)} -> +{added}", flush=True)

    rows = list(unique)
    if not rows:
        print("[warn] No triplets matched in any file.", flush=True)
        sys.exit(0)

    if not args.no_sort:
        rows.sort(key=lambda r: (r[0], r[1], r[2]))

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["IdAplicacion", "IdServicio", "IdTransaccion"])
        w.writerows(rows)

    print(f"[done] Files scanned: {len(files)} | Unique rows: {len(rows)}", flush=True)
    print(f"[done] CSV: {out}", flush=True)

if __name__ == "__main__":
    main()
