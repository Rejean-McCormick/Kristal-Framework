"""Read-only, local compatibility checks for UNESCO companion profile."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_unesco_single_spine_profile():
    profile=json.loads((ROOT/'spec/v7/reference-kos/unesco-thesaurus-profile.json').read_text())
    schema=json.loads((ROOT/'profiles/unesco/kristal-unesco-classification.schema.json').read_text())
    domains=[d['notation'] for d in profile['domains']]
    micros=[mt['notation'] for d in profile['domains'] for mt in d['microthesauri']]
    assert len(domains)==7 and len(micros)==88
    assert set(schema['properties']['domains']['items']['enum'])==set(domains)
    assert set(schema['properties']['microthesauri']['items']['enum'])==set(micros)
    assert 'isced' not in schema['properties']
    assert schema['properties']['kos_id']['const']=='kos:unesco-thesaurus'
