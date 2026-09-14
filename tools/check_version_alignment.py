#!/usr/bin/env python3
"""Check that the Kristal v5 tree contains no accidental legacy release markers."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "README.md", ROOT / "mkdocs.yml", ROOT / "docs" / "Technical-Reference" / "kristal-docs-v5"]
PATTERNS = [
    re.compile(r"\bKristal v[1-4]\b", re.I),
    re.compile(r"\bkristal-v[1-4]\b", re.I),
    re.compile(r"docs/en/"),
    re.compile(r"https://example\.com/kristal-framework"),
]

def main() -> int:
    findings=[]
    for target in TARGETS:
        paths=[target] if target.is_file() else list(target.rglob("*"))
        for p in paths:
            if not p.is_file() or p.suffix.lower() not in {".md", ".yml", ".yaml", ".json", ".txt"}:
                continue
            try: text=p.read_text(encoding="utf-8")
            except UnicodeDecodeError: continue
            for n,line in enumerate(text.splitlines(),1):
                for pattern in PATTERNS:
                    if pattern.search(line):
                        findings.append(f"{p.relative_to(ROOT)}:{n}: {line.strip()}")
    if findings:
        print("Version/alignment violations:")
        print("\n".join(findings))
        return 1
    print("version alignment: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
