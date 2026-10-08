#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION=(ROOT/'VERSION').read_text().strip()
NAME=f'kristal-{VERSION}'
OUT=ROOT.parent/f'{NAME}.zip'
EXCLUDE={'.git','.venv','node_modules','site','dist','__pycache__','.pytest_cache','.kristaldiag','.levelupdiag'}

def eligible(p:Path)->bool:
    return p.is_file() and not any(x in EXCLUDE for x in p.relative_to(ROOT).parts) and p.name!='REPO_MANIFEST.json'
files=sorted((p for p in ROOT.rglob('*') if eligible(p)),key=lambda x:x.relative_to(ROOT).as_posix())
manifest=[]
for p in files:
    b=p.read_bytes(); manifest.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
(ROOT/'REPO_MANIFEST.json').write_text(json.dumps({'format':'kristal.repo-manifest/v1','version':VERSION,'files':manifest},indent=2)+'\n')
files=sorted((p for p in ROOT.rglob('*') if p.is_file() and not any(x in EXCLUDE for x in p.relative_to(ROOT).parts)),key=lambda x:x.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:
        rel=f'{NAME}/{p.relative_to(ROOT).as_posix()}'; data=p.read_bytes()
        info=zipfile.ZipInfo(rel,date_time=(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
        mode=0o100755 if (p.stat().st_mode & 0o111) else 0o100644
        info.external_attr=(mode&0xffff)<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(OUT)
print('sha256',hashlib.sha256(OUT.read_bytes()).hexdigest())
print('files',len(files))
