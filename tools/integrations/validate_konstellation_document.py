"""Schema admission for the optional Konstellation publisher (stdin JSON)."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
root=Path(__file__).resolve().parents[1]/'docs/Technical-Reference/kristal-docs-v5/02-schemas'
names={'policy':'reader-policy.schema.json','manifest':'runtime-pack-manifest.schema.json'}
try:
    schema=json.loads((root/names[sys.argv[1]]).read_text())
    Draft202012Validator(schema,format_checker=FormatChecker()).validate(json.load(sys.stdin))
except Exception as e:
    print(str(e),file=sys.stderr)
    raise SystemExit(1)
