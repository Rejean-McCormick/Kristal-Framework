#!/usr/bin/env python3
"""Check active Kristal v6 release/version markers without flagging retained v5 legacy docs."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ACTIVE=[ROOT/'README.md',ROOT/'mkdocs.yml',ROOT/'docs'/'index.md',ROOT/'docs'/'Technical-Reference'/'kristal-docs-v6']

def main():
    findings=[]
    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    if version!='6.0.0': findings.append(f'VERSION: expected 6.0.0, got {version}')
    release=json.loads((ROOT/'kristal-release.json').read_text(encoding='utf-8'))
    if release.get('core_version')!='6.0': findings.append('kristal-release.json core_version != 6.0')
    if release.get('canonicalization_profile')!='kristal.v6:jcs-rfc8785': findings.append('active canonicalization profile is not v6')
    for target in ACTIVE:
        paths=[target] if target.is_file() else list(target.rglob('*'))
        for p in paths:
            if not p.is_file() or p.suffix.lower() not in {'.md','.yml','.yaml','.json','.txt'}: continue
            text=p.read_text(encoding='utf-8',errors='ignore')
            # Active v6 docs may mention v5 only when clearly marked as legacy/migration/compatibility.
            for n,line in enumerate(text.splitlines(),1):
                if re.search(r'\bActive baseline:\s*Kristal Standard 5|site_name:\s*Kristal Framework v5',line,re.I):
                    findings.append(f'{p.relative_to(ROOT)}:{n}: stale active v5 baseline: {line.strip()}')
    if findings:
        print('Version/alignment violations:'); print('\n'.join(findings)); return 1
    print('version alignment: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
