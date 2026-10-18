#!/usr/bin/env python3
"""Kristal v11 draft.3 offline dictionary import, audit and lookup.

File backed, namespace-scoped and deterministic. No automatic Wikidata equivalence,
translation or semantic identity creation. SQLite is only a temporary import index.
"""
from __future__ import annotations
import argparse
import bz2
import gzip
import hashlib
import json
import re
import sqlite3
import sys
import tempfile
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / 'schemas' / 'v11'
LANGUAGE = re.compile(r'^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$')

class DictionaryError(ValueError):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def check_schema(data, name):
    schema = read_json(SCHEMAS/name)
    errs = list(Draft202012Validator(schema).iter_errors(data))
    if errs:
        err = errs[0]
        raise DictionaryError(f'{name} at {err.json_path}: {err.message}')


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as src:
        for chunk in iter(lambda: src.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def check_locale(tag):
    if not LANGUAGE.fullmatch(tag):
        raise DictionaryError(f'Invalid locale syntax: {tag}')
    # This verifies BCP47-like syntax, not IANA/CLDR registration.
    return tag


def safe_file(base, rel):
    r = Path(rel)
    if r.is_absolute() or '..' in r.parts or not rel or '\\' in rel:
        raise DictionaryError(f'unsafe dictionary path: {rel}')
    target = (base/r).resolve()
    if not target.is_relative_to(base.resolve()):
        raise DictionaryError(f'dictionary path escapes root: {rel}')
    if not target.is_file():
        raise DictionaryError(f'not a file: {rel}')
    return target


def accepted_exact(crosswalk, namespace):
    check_schema(crosswalk, 'kristal-external-crosswalk.schema.json')
    by_external, by_local = {}, {}
    for mapping in crosswalk['mappings']:
        if mapping['status'] != 'accepted' or mapping['relation'] != 'exactMatch':
            continue
        local = mapping['local_ref']
        if local['namespace_id'] != namespace:
            continue
        external = mapping['external_ref']
        xid, kid = external['id'], local['id']
        if (kid.startswith('KQ') != xid.startswith('Q')):
            raise DictionaryError('Q/KQ or P/KP identity kind mismatch')
        if xid in by_external or kid in by_local:
            raise DictionaryError('duplicate accepted exact Wikidata correspondence')
        by_external[xid], by_local[kid] = kid, xid
    return by_external, by_local


def open_dump(path):
    name = str(path)
    return (bz2.open if name.endswith('.bz2') else gzip.open if name.endswith('.gz') else open)(path, 'rt', encoding='utf-8')


def stream_entities(path):
    # Wikidata's official JSON array dump is one entity per line; also accept JSONL.
    with open_dump(path) as handle:
        for line_num,line in enumerate(handle,1):
            line=line.strip()
            if not line or line in ('[',']'):
                continue
            if line.endswith(','):
                line=line[:-1].rstrip()
            try:
                data = json.loads(line)
            except ValueError as e:
                raise DictionaryError(f'invalid JSON entity on line {line_num}: {e}') from e
            if not isinstance(data,dict):
                raise DictionaryError(f'expected JSON entity object on line {line_num}')
            yield data


def source_value(value):
    if isinstance(value,dict) and isinstance(value.get('value'),str):
        return value['value']
    return None


def make_import_record(entity, kid, locale, namespace, snapshot):
    label = source_value(entity.get('labels',{}).get(locale))
    if not label:
        return None
    aliases = []
    for alias in entity.get('aliases',{}).get(locale,[]):
        term = source_value(alias)
        if term and term!=label and term not in aliases:
            aliases.append(term)
    record = {
        'namespace_id':namespace, 'semantic_id':kid, 'external_id':entity['id'],
        'language':locale, 'preferred_term':label, 'aliases':aliases,
        'source_snapshot':snapshot,
    }
    description=source_value(entity.get('descriptions',{}).get(locale))
    if description:
        record['description']=description
    if isinstance(entity.get('lastrevid'),int):
        record['source_revision']=entity['lastrevid']
    check_schema(record,'kristal-wikidata-lexical-record.schema.json')
    return record


def import_local(args):
    catalog_path=Path(args.output)/'catalog.json'
    if catalog_path.exists():
        raise DictionaryError('output catalog already exists; import to a new snapshot directory, do not overwrite existing layers')
    crosswalk=read_json(args.crosswalk)
    ext,_=accepted_exact(crosswalk,args.namespace)
    locales=[check_locale(tag.strip()) for tag in args.languages.split(',')]
    if not locales or len(set(locales))!=len(locales):
        raise DictionaryError('languages must be unique and nonempty')
    outdir=Path(args.output)
    if not re.fullmatch(r'[A-Za-z0-9._-]+',args.snapshot) or args.snapshot in ('.','..'):
        raise DictionaryError('snapshot ID must be a simple safe filename component')
    outdir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        db=sqlite3.connect(str(Path(tmp)/'import.sqlite'))
        db.execute('CREATE TABLE words(lang TEXT NOT NULL, kid TEXT NOT NULL, record TEXT NOT NULL, PRIMARY KEY(lang,kid))')
        seen=0;matched=0
        for entity in stream_entities(args.dump):
            seen+=1
            kid=ext.get(entity.get('id'))
            if not kid:
                continue
            matched+=1
            for locale in locales:
                record=make_import_record(entity,kid,locale,args.namespace,args.snapshot)
                if record is None:
                    continue
                payload=json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(',',':'))
                try:
                    db.execute('INSERT INTO words VALUES (?,?,?)',(locale,kid,payload))
                except sqlite3.IntegrityError as e:
                    raise DictionaryError(f'duplicate Wikidata entity/semantic id for {locale}/{kid}') from e
        db.commit()
        languages=[]
        counts={}
        for locale in locales:
            rel=f'imported/wikidata/{args.snapshot}/{locale}.jsonl'
            target=outdir/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('w',encoding='utf-8',newline='\n') as dst:
                for (payload,) in db.execute('SELECT record FROM words WHERE lang=? ORDER BY kid',(locale,)):
                    dst.write(payload+'\n')
            n=db.execute('SELECT COUNT(*) FROM words WHERE lang=?',(locale,)).fetchone()[0]
            counts[locale]=n
            languages.append({'tag':locale,'fallbacks':[],'layers':[{
                'layer_id':f'wikidata-{args.snapshot}-{locale}',
                'kind':'wikidata','priority':100,'path':rel,'sha256':sha256(target),
                'source_snapshot':args.snapshot,
            }]})
        db.close()
    catalog={
        'schema_version':'11.0','artifact_type':'kristal_dictionary_catalog',
        'catalog_id':f'wikidata-import-{args.snapshot}',
        'namespace_id':args.namespace,'languages':languages,
    }
    check_schema(catalog,'kristal-dictionary-catalog.schema.json')
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'entities_scanned':seen,'accepted_exact_entities_seen':matched,
            'labels_by_locale':counts,
            'catalog':str(catalog_path)}


def layer_records(path,kind):
    if kind=='curated':
        curated=read_json(path)
        check_schema(curated,'kristal-curated-dictionary.schema.json')
        for entry in curated['entries']:
            yield entry,curated
    else:
        with path.open('r',encoding='utf-8') as f:
            for ln,line in enumerate(f,1):
                if not line.strip():continue
                try:
                    entry=json.loads(line)
                except ValueError as e:
                    raise DictionaryError(f'{path.name}:{ln}: invalid JSONL: {e}') from e
                check_schema(entry, 'kristal-external-lexical-record.schema.json' if kind=='external' else 'kristal-wikidata-lexical-record.schema.json')
                yield entry,None


def audit(catalog_path, crosswalk_path=None, registry_path=None):
    catalog=read_json(catalog_path)
    check_schema(catalog,'kristal-dictionary-catalog.schema.json')
    ns=catalog['namespace_id']
    base=Path(catalog_path).resolve().parent
    allowed_by_local=None
    if crosswalk_path:
        _,allowed_by_local=accepted_exact(read_json(crosswalk_path),ns)
    registered=None
    if registry_path:
        registry=read_json(registry_path)
        check_schema(registry,'kristal-identity-registry.schema.json')
        if registry['namespace_id']!=ns:
            raise DictionaryError('registry namespace mismatch')
        registered={x['id'] for x in registry['identities']}
    nlang=set(); totals={}
    for lang in catalog['languages']:
        tag=check_locale(lang['tag'])
        if tag in nlang:raise DictionaryError('duplicate locale in catalog')
        nlang.add(tag)
        if tag in lang['fallbacks'] or len(set(lang['fallbacks']))!=len(lang['fallbacks']):
            raise DictionaryError('invalid locale fallback')
    fallbacks={x['tag']:x['fallbacks'] for x in catalog['languages']}
    def visit(tag, stack):
        if tag in stack:
            raise DictionaryError('cyclic locale fallback: ' + ' -> '.join(stack+[tag]))
        for next_tag in fallbacks[tag]:
            if next_tag in fallbacks:
                visit(next_tag,stack+[tag])
    for tag in fallbacks:
        visit(tag,[])
    for lang in catalog['languages']:
        if any(f not in nlang for f in lang['fallbacks']):
            raise DictionaryError('fallback locale absent from catalog')
        seen_layer_id=set(); layer_total=0
        priority_index={}
        for layer in lang['layers']:
            if layer['layer_id'] in seen_layer_id:
                raise DictionaryError('duplicate layer ID in locale')
            seen_layer_id.add(layer['layer_id'])
            p=safe_file(base,layer['path'])
            if sha256(p)!=layer['sha256']:
                raise DictionaryError(f'layer digest mismatch: {layer["path"]}')
            seen_refs=set()
            for entry,parent in layer_records(p,layer['kind']):
                kid=entry['semantic_id']
                if kid in seen_refs:
                    raise DictionaryError(f'duplicate KQ/KP in one layer {layer["path"]}: {kid}')
                seen_refs.add(kid)
                key=(layer['priority'],kid)
                previous=priority_index.get(key)
                if previous is not None and previous != entry['preferred_term']:
                    raise DictionaryError(f'conflicting same-priority lexical terms: {lang["tag"]}/{kid}')
                priority_index[key]=entry['preferred_term']
                if registry_path and kid not in registered:
                    raise DictionaryError(f'unknown Kristal identity {kid}')
                if layer['kind']=='wikidata':
                    if entry['namespace_id']!=ns or entry['language']!=lang['tag'] or entry['source_snapshot']!=layer['source_snapshot']:
                        raise DictionaryError('imported record namespace/locale/snapshot mismatch')
                    if allowed_by_local is not None and allowed_by_local.get(kid)!=entry['external_id']:
                        raise DictionaryError('unaccepted or stale Wikidata crosswalk')
                elif layer['kind']=='external':
                    if (entry['namespace_id']!=ns or entry['language']!=lang['tag']
                        or entry['source_snapshot']!=layer['source_snapshot']
                        or entry['source_system']!=layer['source_system']
                        or entry['license']!=layer['license']):
                        raise DictionaryError('external dictionary record provenance mismatch')
                    if registry_path:
                        src_ids={x['id']:x['kind'] for x in registry['identities']}
                        for proof in entry['alignment']['evidence_refs']:
                            if src_ids.get(proof)!='source':
                                raise DictionaryError('external alignment evidence KS absent from registry')
                else:
                    if parent['namespace_id']!=ns or parent['language']!=lang['tag']:
                        raise DictionaryError('curated file namespace/locale mismatch')
                for term in [entry['preferred_term']]+entry.get('aliases',entry.get('alternate_terms',[])):
                    if unicodedata.normalize('NFC',term)!=term:
                        raise DictionaryError('lexical text must be NFC normalized')
                layer_total+=1
        totals[lang['tag']]=layer_total
    return {'catalog':str(catalog_path),'locales':len(nlang),'records_by_locale':totals}


def resolve(catalog_path, semantic_id, locale):
    catalog=read_json(catalog_path)
    check_schema(catalog,'kristal-dictionary-catalog.schema.json')
    langs={x['tag']:x for x in catalog['languages']}
    if locale not in langs:
        return {'status':'missing','semantic_id':semantic_id,'requested_locale':locale}
    for effective in [locale]+langs[locale]['fallbacks']:
        group=langs[effective]
        candidates=[]
        for layer in group['layers']:
            path=safe_file(Path(catalog_path).resolve().parent,layer['path'])
            for entry,_ in layer_records(path,layer['kind']):
                if entry['semantic_id']==semantic_id:
                    candidates.append((layer['priority'],entry['preferred_term'],layer['layer_id']))
        if candidates:
            highest=max(p for p,_,_ in candidates)
            winners=[(term,layer) for p,term,layer in candidates if p==highest]
            if len({term for term,_ in winners})!=1:
                return {'status':'conflicted','semantic_id':semantic_id,'requested_locale':locale,
                        'effective_locale':effective,'candidates':winners}
            return {'status':'resolved','semantic_id':semantic_id,'requested_locale':locale,
                    'effective_locale':effective,'fallback':effective!=locale,
                    'term':winners[0][0],'layer':winners[0][1]}
    return {'status':'missing','semantic_id':semantic_id,'requested_locale':locale}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    imp=sub.add_parser('import-local',help='stream Wikidata JSON/JSONL local mirror; accepted exact mappings only')
    for key,opts in [('dump',{}),('crosswalk',{}),('namespace',{}),('snapshot',{}),('languages',{}),('output',{})]:
        imp.add_argument('--'+key,required=True,**opts)
    aud=sub.add_parser('audit',help='validate catalog, file hashes, locales and optional references')
    aud.add_argument('--catalog',required=True)
    aud.add_argument('--crosswalk')
    aud.add_argument('--registry')
    res=sub.add_parser('resolve',help='resolve display term without modifying graph')
    res.add_argument('--catalog',required=True)
    res.add_argument('--id',required=True)
    res.add_argument('--locale',required=True)
    args=parser.parse_args()
    try:
        if args.command=='import-local':result=import_local(args)
        elif args.command=='audit':result=audit(args.catalog,args.crosswalk,args.registry)
        else:result=resolve(args.catalog,args.id,args.locale)
    except (DictionaryError,OSError,KeyError,json.JSONDecodeError) as e:
        raise SystemExit(f'Kristal dictionary operation failed: {e}') from e
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
