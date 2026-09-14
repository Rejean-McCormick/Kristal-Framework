#!/usr/bin/env python3
"""Check MkDocs navigation targets and local Markdown file links."""
from __future__ import annotations
import re
import urllib.parse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def nav_paths(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from nav_paths(item)
    elif isinstance(node, dict):
        for value in node.values():
            yield from nav_paths(value)


def check_nav(errors: list[str]) -> None:
    cfg = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    if cfg.get("docs_dir", "docs") != "docs":
        errors.append("mkdocs.yml: docs_dir must remain 'docs' for this release layout")
    for rel in nav_paths(cfg.get("nav", [])):
        if rel.startswith(("http://", "https://")):
            continue
        target = DOCS / rel
        if not target.is_file():
            errors.append(f"mkdocs nav target missing: {rel}")


def normalize_link(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith('<') and raw.endswith('>'):
        raw = raw[1:-1]
    # Ignore optional Markdown title after a whitespace separator.
    if ' "' in raw:
        raw = raw.split(' "', 1)[0]
    return urllib.parse.unquote(raw)


def check_markdown_links(errors: list[str]) -> None:
    files = [ROOT / "README.md", ROOT / "CHANGELOG.md", ROOT / "RELEASE.md"] + list(DOCS.rglob("*.md"))
    for p in files:
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), 1):
            for m in LINK_RE.finditer(line):
                dest = normalize_link(m.group(1))
                if not dest or dest.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                file_part = dest.split('#', 1)[0]
                if not file_part:
                    continue
                if file_part.startswith('/'):
                    continue
                target = (p.parent / file_part).resolve()
                try:
                    target.relative_to(ROOT.resolve())
                except ValueError:
                    errors.append(f"{p.relative_to(ROOT)}:{line_no}: link escapes repository: {dest}")
                    continue
                if not target.exists():
                    errors.append(f"{p.relative_to(ROOT)}:{line_no}: missing local link target: {dest}")


def main() -> int:
    errors=[]
    check_nav(errors)
    check_markdown_links(errors)
    if errors:
        print("Documentation validation failures:")
        print("\n".join(errors))
        return 1
    print("documentation navigation and local links: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
