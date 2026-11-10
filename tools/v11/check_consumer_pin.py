#!/usr/bin/env python3
"""Framework-owned, read-only verification of a consumer's draft.4 source pin.

This checks *local source bytes*, not product conformance, authenticity of a
remote checkout, a release signature, publication, or deployment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
PROFILE='kristal-integration-framework-pin/v11.0-draft.4'

class ConsumerPinError(ValueError):
    pass

def verify_consumer_pin(consumer_pin:Path, framework:Path=ROOT)->dict:
    pinfile=Path(consumer_pin).resolve()
    fw=Path(framework).resolve()
    if not pinfile.is_file():raise ConsumerPinError('Missing consumer pin file')
    data=json.loads(pinfile.read_text(encoding='utf-8'))
    if data.get('profile')!=PROFILE or data.get('version')!='11.0.0-draft.4':
        raise ConsumerPinError('Consumer pin version/profile mismatch')
    if not (fw/'VERSION').is_file() or (fw/'VERSION').read_text(encoding='utf-8').strip()!=data['version']:
        raise ConsumerPinError('Framework local source version mismatch')
    files=data.get('files')
    if not isinstance(files,dict) or len(files)!=13:
        raise ConsumerPinError('Expected complete 13-file Framework pin')
    for name,digest in files.items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name or not re.fullmatch('[a-f0-9]{64}',str(digest)):
            raise ConsumerPinError('Invalid or unsafe pin path: '+str(name))
        actual=(fw/p).resolve()
        if not actual.is_relative_to(fw) or not actual.is_file() or hashlib.sha256(actual.read_bytes()).hexdigest()!=digest:
            raise ConsumerPinError('Consumer Framework pin mismatch: '+name)
    return {'profile':'kristal.framework-consumer-pin-observation/1.0',
            'framework_version':data['version'],'files_matched':len(files),
            'local_source_bytes_match':True,'read_only':True,
            'qualification':'source-hash-match-only; no authority to register, publish or activate'}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consumer-pin',type=Path,required=True)
    parser.add_argument('--framework',type=Path,default=ROOT)
    args=parser.parse_args(argv)
    try: result=verify_consumer_pin(args.consumer_pin,args.framework)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        parser.exit(1,'Framework consumer pin REFUSED: '+str(exc)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
