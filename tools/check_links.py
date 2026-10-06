#!/usr/bin/env python3
from __future__ import annotations
import re, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LINK_RE=re.compile(r'\[[^\]]*\]\(([^)]+)\)')

def main():
    errors=[]
    for p in [ROOT/'README.md',ROOT/'MIGRATION.md',ROOT/'GOVERNANCE.md',*ROOT.glob('spec/**/*.md'),*ROOT.glob('docs/**/*.md'),*ROOT.glob('reference/**/*.md')]:
        if not p.is_file(): continue
        for n,line in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
            for raw in LINK_RE.findall(line):
                dest=raw.strip().split(' "',1)[0]
                if not dest or dest.startswith(('#','http://','https://','mailto:')): continue
                part=urllib.parse.unquote(dest.split('#',1)[0])
                if not part or part.startswith('/'): continue
                target=(p.parent/part).resolve()
                try: target.relative_to(ROOT.resolve())
                except ValueError:
                    errors.append(f'{p.relative_to(ROOT)}:{n}: link escapes repo: {dest}'); continue
                if not target.exists(): errors.append(f'{p.relative_to(ROOT)}:{n}: missing link: {dest}')
    if errors:
        print('\n'.join(errors)); return 1
    print('documentation local links: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
