# v11 TCK vectors

Positive JSON examples mirror `examples/v11/`. The negative vectors live in `tools/tests/test_v11_semantics.py` and are executed through `python tools/v11/validate_v11.py` and `python -m unittest discover -s tools/tests -p 'test_v11_*.py'`.

The IDs are demonstrations only, not production-issued identifiers. The frozen v6–v10 TCK files have not been changed.

Draft.3 includes a deterministic diK graph-language coverage vector and a pending-only conversion plan fixture, tested with `test_v11_dik_contracts.py`. These fixtures do not authorize source changes.
