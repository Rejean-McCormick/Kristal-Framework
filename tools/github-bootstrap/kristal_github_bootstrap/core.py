from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import uuid
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

API_VERSION = "2026-03-10"
BOOTSTRAP_VERSION = "1.1.0-alpha.10"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

# Pinned, verified upstream release commits (2026-10-07).
ACTION_CHECKOUT = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"  # v4.4.0
ACTION_SETUP_NODE = "actions/setup-node@820762786026740c76f36085b0efc47a31fe5020"  # v7.0.0
ACTION_ATTEST = "actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6"  # v4.2.2
ACTION_UPLOAD_ARTIFACT = "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9"  # v7.0.2


class BootstrapError(RuntimeError):
    pass


def _text(value: Any) -> str:
    """Normalize subprocess/API diagnostic text. Windows wrappers can occasionally surface None."""
    if value is None:
        return ""
    return value if isinstance(value, str) else str(value)


class GitHubApiError(BootstrapError):
    def __init__(self, method: str, endpoint: str, stderr: str | None, status: int | None = None):
        stderr_text = _text(stderr)
        self.method, self.endpoint, self.stderr, self.status = method, endpoint, stderr_text, status
        kind = "not_found" if status == 404 else "forbidden" if status == 403 else "rate_limited" if status == 429 else "api_error"
        self.kind = kind
        detail = stderr_text.strip() or "GitHub CLI returned no diagnostic text"
        super().__init__(f"GitHub API {method} {endpoint} failed ({kind}{f' HTTP {status}' if status else ''}):\n{detail}")


@dataclass(frozen=True)
class RepoSpec:
    name: str
    visibility: str
    role: str
    node_id: str
    description: str = ""
    collection: str | None = None
    identity_key: str | None = None


class GhClient:
    """Small gh(1) adapter. No token or secret is persisted."""

    def __init__(self, api_version: str = API_VERSION, dry_run: bool = False):
        self.api_version = api_version
        self.dry_run = dry_run

    def _run(self, argv: list[str], stdin: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
        kwargs: dict[str, Any] = {}
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        p = subprocess.run(argv, input=stdin, text=True, capture_output=True, **kwargs)
        if check and p.returncode:
            raise BootstrapError(f"command failed ({p.returncode}): {' '.join(argv)}\n{_text(p.stderr).strip() or 'no diagnostic text'}")
        return p

    def doctor(self) -> dict[str, Any]:
        gh = self._run(["gh", "--version"])
        auth = self._run(["gh", "auth", "status"], check=False)
        user = self.api("GET", "/user") if auth.returncode == 0 else None
        gh_out = _text(gh.stdout).strip()
        auth_err = _text(auth.stderr).strip()
        return {"gh": gh_out.splitlines()[0] if gh_out else "gh (version output unavailable)", "authenticated": auth.returncode == 0, "user": user, "auth_diagnostic": auth_err or None}

    @staticmethod
    def _status(stderr: str | None) -> int | None:
        stderr = _text(stderr)
        m = re.search(r"HTTP\s+(\d{3})", stderr, re.I)
        if m:
            return int(m.group(1))
        m = re.search(r"status(?: code)?[: ]+(\d{3})", stderr or "", re.I)
        return int(m.group(1)) if m else None

    def api(self, method: str, endpoint: str, body: dict[str, Any] | None = None, optional: bool = False) -> Any:
        argv = ["gh", "api", "-H", "Accept: application/vnd.github+json", "-H", f"X-GitHub-Api-Version: {self.api_version}", "--method", method, endpoint]
        stdin = None
        if body is not None:
            argv += ["--input", "-"]
            stdin = json.dumps(body)
        if self.dry_run and method != "GET":
            return {"dry_run": True, "method": method, "endpoint": endpoint, "body": body}
        p = self._run(argv, stdin=stdin, check=False)
        if p.returncode:
            status = self._status(p.stderr)
            if optional and status == 404:
                return None
            raise GitHubApiError(method, endpoint, p.stderr, status)
        stdout = _text(p.stdout)
        if not stdout.strip():
            return None
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return stdout.strip()

    def repo(self, owner: str, name: str) -> dict[str, Any] | None:
        return self.api("GET", f"/repos/{owner}/{name}", optional=True)

    def create_repo(self, owner: str, account_kind: str, spec: RepoSpec) -> Any:
        body: dict[str, Any] = {"name": spec.name, "description": spec.description, "has_issues": True, "has_projects": False, "has_wiki": False, "auto_init": True}
        if spec.visibility == "internal":
            body["visibility"] = "internal"
        else:
            body["private"] = spec.visibility == "private"
        endpoint = f"/orgs/{owner}/repos" if account_kind == "organization" else "/user/repos"
        return self.api("POST", endpoint, body)

    def get_text_file(self, owner: str, repo: str, path: str) -> tuple[str, str] | None:
        current = self.api("GET", f"/repos/{owner}/{repo}/contents/{path}", optional=True)
        if not isinstance(current, dict) or "content" not in current:
            return None
        return base64.b64decode(current["content"]).decode(), current.get("sha", "")

    def put_text_file(self, owner: str, repo: str, path: str, content: str, message: str, branch: str | None = None, overwrite_managed: bool = False) -> str:
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        existing = self.api("GET", endpoint, optional=True)
        if existing and not overwrite_managed:
            return "kept"
        body = {"message": message, "content": base64.b64encode(content.encode()).decode()}
        if branch:
            body["branch"] = branch
        if existing and isinstance(existing, dict) and existing.get("sha"):
            body["sha"] = existing["sha"]
        self.api("PUT", endpoint, body)
        return "updated" if existing else "created"


def load_config(path: Path) -> dict[str, Any]:
    import tomllib
    with path.open("rb") as f:
        cfg = tomllib.load(f)
    validate_config(cfg)
    return cfg


def framework(cfg: dict[str, Any]) -> tuple[str, str]:
    f = cfg.get("framework", {})
    repo = f.get("repository") or f"{cfg['account']['owner']}/KristalV10"
    ref = f.get("ref", "")
    return repo, ref


def _network_id(cfg: dict[str, Any]) -> str:
    return cfg.get("network", {}).get("id") or f"urn:kristal:network:{cfg['account']['owner']}"


def stable_node_id(cfg: dict[str, Any], identity_key: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    u = uuid.uuid5(uuid.NAMESPACE_URL, f"{_network_id(cfg)}\u0000{identity_key}")
    return f"urn:uuid:{u}"


def node_id(owner: str, repo: str) -> str:
    """Legacy helper retained for source compatibility; new configs use stable_node_id()."""
    return f"urn:kristal:node:github:{owner}:{repo}"


def validate_config(cfg: dict[str, Any]) -> None:
    account = cfg.get("account", {})
    if account.get("kind") not in {"user", "organization"}:
        raise BootstrapError("account.kind must be 'user' or 'organization'")
    if not account.get("owner"):
        raise BootstrapError("account.owner is required")

    collections = cfg.get("collections", [])
    if not collections:
        raise BootstrapError("at least one [[collections]] entry is required")
    vis = {c.get("visibility") for c in collections}
    if "public" not in vis or "private" not in vis:
        raise BootstrapError("initial topology must contain at least one public and one private collection")
    for c in collections:
        if c.get("visibility") not in {"public", "private", "internal"}:
            raise BootstrapError(f"invalid collection visibility for {c.get('name')}")
        if c.get("visibility") == "internal" and account.get("kind") != "organization":
            raise BootstrapError("internal visibility requires account.kind='organization'")
        if not c.get("name"):
            raise BootstrapError("every collection requires name")
        if c.get("role", "collection") not in {"collection", "directory", "gateway", "publisher"}:
            raise BootstrapError(f"invalid collection role for {c.get('name')}")

    hub = cfg.get("hub", {})
    if not hub.get("repository"):
        raise BootstrapError("hub.repository is required")
    if hub.get("visibility", "private") == "public" and any(c.get("visibility") != "public" for c in collections):
        raise BootstrapError("a public all-node hub would disclose private collection metadata; use a private hub")

    names = [hub["repository"]] + [c["name"] for c in collections]
    g = cfg.get("global", {})
    if g.get("create_dotgithub", True): names.append(".github")
    if account["kind"] == "organization" and g.get("create_private_profile", True): names.append(".github-private")
    if account["kind"] == "user" and g.get("create_profile_repository", True): names.append(account["owner"])
    folded = [n.casefold() for n in names]
    if len(folded) != len(set(folded)):
        raise BootstrapError("repository name collision across global/hub/collections topology")

    identities = [c.get("identity_key", c["name"]) for c in collections]
    if len(identities) != len(set(identities)):
        raise BootstrapError("collections.identity_key values must be unique")

    feature_modes = {"off", "best_effort", "required"}
    for feature in ("immutable_releases", "environments", "custom_properties", "attestations"):
        mode = cfg.get("features", {}).get(feature, "best_effort")
        if mode not in feature_modes:
            raise BootstrapError(f"features.{feature} must be one of: off, best_effort, required")

    fw, ref = framework(cfg)
    if "/" not in fw or any(not part.strip() for part in fw.split("/", 1)):
        raise BootstrapError("framework.repository must be OWNER/REPOSITORY")
    if not SHA_RE.fullmatch(ref or ""):
        raise BootstrapError("framework.ref must be a full 40-character commit SHA; floating refs are not accepted")


def desired_repos(cfg: dict[str, Any]) -> list[RepoSpec]:
    a, owner = cfg["account"], cfg["account"]["owner"]
    out: list[RepoSpec] = []
    g = cfg.get("global", {})
    if g.get("create_dotgithub", True): out.append(RepoSpec(".github", "public", "global", stable_node_id(cfg, "global:.github"), "Account-wide Kristal GitHub integration", identity_key="global:.github"))
    if a["kind"] == "organization" and g.get("create_private_profile", True): out.append(RepoSpec(".github-private", "private", "global-private", stable_node_id(cfg, "global:.github-private"), "Member-only Kristal organization profile", identity_key="global:.github-private"))
    if a["kind"] == "user" and g.get("create_profile_repository", True): out.append(RepoSpec(owner, "public", "profile", stable_node_id(cfg, "global:profile"), "GitHub profile with Kristal network discovery", identity_key="global:profile"))
    hub = cfg["hub"]
    out.append(RepoSpec(hub["repository"], hub.get("visibility", "private"), "directory", stable_node_id(cfg, hub.get("identity_key", "root-directory"), hub.get("node_id")), "Private root directory for the Kristal network", identity_key=hub.get("identity_key", "root-directory")))
    for c in cfg["collections"]:
        key = c.get("identity_key", c["name"])
        out.append(RepoSpec(c["name"], c["visibility"], c.get("role", "collection"), stable_node_id(cfg, key, c.get("node_id")), c.get("description", f"Kristal collection: {c['name']}"), c.get("collection", c["name"]), key))
    return out


def _existing_node_id(client: GhClient, owner: str, repo: str) -> str | None:
    try:
        got = client.get_text_file(owner, repo, ".kristal/node.json")
    except AttributeError:
        return None
    if not got: return None
    try:
        doc = json.loads(got[0]); nid = doc.get("node_id")
        return nid if isinstance(nid, str) and nid else None
    except Exception:
        return None


def hydrate_existing_node_ids(client: GhClient, cfg: dict[str, Any], specs: list[RepoSpec]) -> list[RepoSpec]:
    owner = cfg["account"]["owner"]
    return [replace(s, node_id=_existing_node_id(client, owner, s.name) or s.node_id) for s in specs]


def account_preflight(client: GhClient, cfg: dict[str, Any], required: bool = False) -> dict[str, Any]:
    owner, kind = cfg["account"]["owner"], cfg["account"]["kind"]
    if kind != "user": return {"status":"ok","kind":kind,"owner":owner}
    try: current = client.api("GET", "/user")
    except Exception:
        if required: raise
        return {"status":"unresolved","kind":kind,"owner":owner}
    login = current.get("login") if isinstance(current, dict) else None
    ok = isinstance(login, str) and login.casefold() == owner.casefold()
    if required and not ok: raise BootstrapError(f"authenticated GitHub user {login!r} does not match account.owner {owner!r}")
    return {"status":"ok" if ok else "blocked","kind":kind,"owner":owner,"authenticated_login":login}


def framework_preflight(client: GhClient, cfg: dict[str, Any], *, required: bool = False) -> dict[str, Any]:
    slug, ref = framework(cfg)
    fw_owner, fw_repo = slug.split("/", 1)
    current = client.repo(fw_owner, fw_repo)
    result: dict[str, Any] = {"repository": slug, "ref": ref}
    if not current:
        result.update(status="unresolved", usable_from_public_nodes=False, ref_resolved=False, reason="repository_not_accessible")
        if required:
            raise BootstrapError(f"framework repository {slug} is not accessible")
        return result

    visibility = current.get("visibility") if isinstance(current, dict) else None
    if visibility is None and isinstance(current, dict) and "private" in current:
        visibility = "private" if current.get("private") else "public"
    has_public_nodes = any(c.get("visibility") == "public" for c in cfg.get("collections", []))
    usable = not has_public_nodes or visibility == "public"

    # A full SHA is an immutable Git object identity. Verify the exact object first
    # through the Git database endpoint, then fall back to the repository commit
    # endpoint because GitHub CLI/API behavior can vary across environments.
    attempts: list[dict[str, Any]] = []
    ref_ok = False
    resolved_sha: str | None = None
    endpoints = [
        f"/repos/{fw_owner}/{fw_repo}/git/commits/{ref}",
        f"/repos/{fw_owner}/{fw_repo}/commits/{ref}",
    ]
    for endpoint in endpoints:
        try:
            commit = client.api("GET", endpoint, optional=True)
            got = str(commit.get("sha", "")).lower() if isinstance(commit, dict) else ""
            ok = got == ref.lower()
            attempts.append({"endpoint": endpoint, "status": "ok" if ok else ("not_found" if commit is None else "sha_mismatch"), "sha": got or None})
            if ok:
                ref_ok = True
                resolved_sha = got
                break
        except GitHubApiError as exc:
            attempts.append({"endpoint": endpoint, "status": exc.kind, "http_status": exc.status, "diagnostic": exc.stderr.strip() or None})
        except BootstrapError as exc:
            attempts.append({"endpoint": endpoint, "status": "error", "diagnostic": str(exc)})

    reason = None
    if not usable:
        reason = "framework_not_public_for_public_nodes"
    elif not ref_ok:
        reason = "framework_commit_not_resolved"
    result.update(
        status="ok" if usable and ref_ok else "blocked",
        visibility=visibility,
        usable_from_public_nodes=usable,
        ref_resolved=ref_ok,
        resolved_sha=resolved_sha,
        reason=reason,
        verification_attempts=attempts,
    )
    if required and not usable:
        raise BootstrapError(f"framework repository {slug} must be public when public Kristal nodes use it without extra credentials")
    if required and not ref_ok:
        detail = json.dumps(attempts, ensure_ascii=False)
        raise BootstrapError(f"framework ref {ref} is not resolvable as the pinned commit in {slug}; attempts={detail}")
    return result


def capabilities_doc(effective: dict[str, str] | None = None) -> dict[str, Any]:
    effective = effective or {}
    return {
        "schema_version":"10.0","artifact_type":"kristal_v10_capabilities",
        "compatibility":{"reads":["kristal_state/6.0","kristall/7.0","kristall/8.0","kristal.state/9.0","kristal.hosting/10.0"],"portable_state":"kristal_state/6.0","semantic_baseline":"kristall/7.0","query_baseline":"kristall/8.0","semantic_state_baseline":"kristal.state/9.0","hosted_network_baseline":"kristal.hosting/10.0"},
        "capabilities":{"semantic_state":{"v9_unchanged":True,"logical_commitments":True,"immutable_snapshots":True},"node_model":{"manifests":True,"bindings":True,"publications":True},"hosting":{"multiple_bindings":True,"profiles":["kristal.host/github/1.0"]},"discovery":{"directories":True,"well_known":False}},
    }


def github_binding(owner: str, account_kind: str, spec: RepoSpec, default_branch: str = "main", effective: dict[str, str] | None = None) -> dict[str, Any]:
    effective = effective or {}
    surfaces: dict[str, Any] = {
        "source":{"kind":"git","locator":f"https://github.com/{owner}/{spec.name}.git"},
        "publication":{"kind":"github-release","locator":f"github-release://{owner}/{spec.name}"},
        "automation":{"kind":"github-actions","locator":f"github-actions://{owner}/{spec.name}"},
        "discovery":{"kind":"repository-file","locator":".kristal/node.json"},
    }
    if effective.get("environment") in {"created","present","created-or-present","required"}: surfaces["activation"]={"kind":"github-environment","locator":f"github-environment://{owner}/{spec.name}/production"}
    if effective.get("attestations") in {"configured","required"}: surfaces["attestation"]={"kind":"github-artifact-attestation","locator":f"github-attestation://{owner}/{spec.name}"}
    return {"schema_version":"10.0","artifact_type":"kristal_host_binding","binding_id":"github-primary","node_id":spec.node_id,"profile":{"id":"kristal.host/github","version":"1.0"},"host":{"provider":"github.com","account_scope":{"kind":account_kind,"owner":owner}},"resource":{"kind":"repository","locator":f"github://{owner}/{spec.name}","visibility":spec.visibility},"surfaces":surfaces,"profile_configuration":{"repository":spec.name,"default_branch":default_branch,"api_version":API_VERSION}}


def node_manifest(spec: RepoSpec, directory: bool = False) -> dict[str, Any]:
    roles=[spec.role];
    if spec.role=="collection": roles.append("publisher")
    if directory and "directory" not in roles: roles.append("directory")
    return {"schema_version":"10.0","artifact_type":"kristal_node_manifest","node_id":spec.node_id,"roles":roles,"semantic_state_contracts":["kristal.state/9.0"],"capabilities":".kristal/capabilities.json","bindings":[{"binding_id":"github-primary","profile":"kristal.host/github/1.0","descriptor":".kristal/bindings/github.json"}]}


def _directory_entry(owner: str, s: RepoSpec) -> dict[str, Any]:
    return {"node_id":s.node_id,"roles":[s.role]+(["publisher"] if s.role=="collection" else []),"bindings":[{"binding_id":"github-primary","profile":"kristal.host/github/1.0","descriptor":f"github://{owner}/{s.name}/.kristal/bindings/github.json"}],"metadata":{"repository":s.name,"visibility":s.visibility,"collection":s.collection or s.name}}


def directory_doc(cfg: dict[str, Any], specs: list[RepoSpec], registry_entries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    owner=cfg["account"]["owner"]; hub_name=cfg["hub"]["repository"]; by_id={}
    for s in specs:
        if s.name!=hub_name and s.role in {"collection","directory","gateway","publisher"}: by_id[s.node_id]=_directory_entry(owner,s)
    for e in registry_entries or []:
        if isinstance(e,dict) and e.get("node_id"): by_id[e["node_id"]]=e
    return {"schema_version":"10.0","artifact_type":"kristal_directory","directory_id":f"urn:kristal:directory:{hashlib.sha256(_network_id(cfg).encode()).hexdigest()[:24]}","node_id":next(s.node_id for s in specs if s.name==hub_name),"entries":sorted(by_id.values(),key=lambda e:e["node_id"])}


def qualify_workflow(cfg: dict[str, Any], include_directory: bool = False) -> str:
    fw, ref=framework(cfg); directory_check = """
      - name: Verify v10 directory
        if: ${{ hashFiles('.kristal/directory.json') != '' }}
        run: node .kristal-framework/reference/js/bin/kristal-ref.mjs verify-directory-v10 .kristal/directory.json
""" if include_directory else ""
    return f'''name: Kristal v10 Qualify

on:
  push:
    paths:
      - '.kristal/**'
      - '.github/workflows/kristal-qualify.yml'
  pull_request:
    paths:
      - '.kristal/**'
      - '.github/workflows/kristal-qualify.yml'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  qualify:
    name: qualify
    runs-on: ubuntu-latest
    steps:
      - uses: {ACTION_CHECKOUT}
      - uses: {ACTION_SETUP_NODE}
        with:
          node-version: '22'
          package-manager-cache: false
      - name: Load pinned Kristal framework
        uses: {ACTION_CHECKOUT}
        with:
          repository: {fw}
          ref: {ref}
          path: .kristal-framework
      - name: Verify v10 node
        run: node .kristal-framework/reference/js/bin/kristal-ref.mjs verify-node-v10 .kristal/node.json
      - name: Verify GitHub host binding
        run: node .kristal-framework/reference/js/bin/kristal-ref.mjs verify-github-binding-v10 .kristal/bindings/github.json
{directory_check}      - name: Emit qualification receipt
        shell: bash
        run: |
          set -euo pipefail
          mkdir -p .kristal/receipts
          jq -n --arg commit "$GITHUB_SHA" --arg framework "{ref}" --arg profile "V10-GitHub-Host/draft.2" '{{schema_version:"1.0",artifact_type:"kristal_qualification_receipt",source_commit:$commit,framework_commit:$framework,profile:$profile,result:"pass"}}' > .kristal/receipts/qualification.json
      - name: Upload qualification receipt
        uses: {ACTION_UPLOAD_ARTIFACT}
        with:
          name: kristal-qualification-${{{{ github.sha }}}}
          path: .kristal/receipts/qualification.json
          if-no-files-found: error
'''


def collection_validator_script() -> str:
    """Return the standalone read-surface validator installed in collection repos."""
    return Path(__file__).with_name("collection_ingest.py").read_text(encoding="utf-8")


def collection_ingest_workflow(cfg: dict[str, Any]) -> str:
    """Validate only changed hosted Kristals, sharded for large collection commits."""
    fw, ref = framework(cfg)
    return f'''name: Kristal Collection Ingest

on:
  push:
    paths:
      - 'kristals/**'
      - '.kristal/tools/validate-read-surface.py'
      - '.github/workflows/kristal-ingest.yml'
  pull_request:
    paths:
      - 'kristals/**'
      - '.kristal/tools/validate-read-surface.py'
      - '.github/workflows/kristal-ingest.yml'
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: kristal-ingest-${{{{ github.repository }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  discover:
    name: discover-and-index
    runs-on: ubuntu-latest
    outputs:
      count: ${{{{ steps.discover.outputs.count }}}}
      shard_size: ${{{{ steps.discover.outputs.shard_size }}}}
      matrix: ${{{{ steps.discover.outputs.matrix }}}}
    steps:
      - uses: {ACTION_CHECKOUT}
        with:
          fetch-depth: 0
      - name: Validate derived collection index
        run: python .kristal/tools/validate-read-surface.py validate-index --repo .
      - name: Discover changed Kristal read surfaces
        id: discover
        shell: bash
        run: |
          set -euo pipefail
          python .kristal/tools/validate-read-surface.py discover --repo . --min-shard-size 50 >> "$GITHUB_OUTPUT"
      - name: Report discovery
        shell: bash
        run: >-
          echo "Changed/read-surface roots: ${{{{ steps.discover.outputs.count }}}}; shard size: ${{{{ steps.discover.outputs.shard_size }}}}"

  validate:
    name: validate-read-surface-${{{{ matrix.id }}}}
    needs: discover
    if: ${{{{ needs.discover.outputs.count != '0' }}}}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      max-parallel: 8
      matrix: ${{{{ fromJSON(needs.discover.outputs.matrix) }}}}
    steps:
      - uses: {ACTION_CHECKOUT}
        with:
          fetch-depth: 0
      - uses: {ACTION_SETUP_NODE}
        with:
          node-version: '22'
          package-manager-cache: false
      - name: Load pinned Kristal framework
        uses: {ACTION_CHECKOUT}
        with:
          repository: {fw}
          ref: {ref}
          path: .kristal-framework
      - name: Validate exact AI/GitHub read-surface shard
        run: >-
          python .kristal/tools/validate-read-surface.py validate-shard
          --repo .
          --shard-id ${{{{ matrix.id }}}}
          --shard-size ${{{{ needs.discover.outputs.shard_size }}}}
          --framework-cli .kristal-framework/reference/js/bin/kristal-ref.mjs
'''


def publish_workflow(cfg: dict[str, Any], attest_mode: str = "best_effort") -> str:
    fw, ref=framework(cfg); env_mode=cfg.get("features",{}).get("environments","best_effort")
    environment_line = "    environment: production\n" if env_mode == "required" else ""
    attest_permissions=""; attest_step=""
    if attest_mode != "off":
        attest_permissions="  id-token: write\n  attestations: write\n  artifact-metadata: write\n"
        cont="true" if attest_mode=="best_effort" else "false"
        attest_step=f'''      - name: Attest publication bundle
        continue-on-error: {cont}
        uses: {ACTION_ATTEST}
        with:
          subject-path: dist/kristal-publication/*
          predicate-type: https://kristal.dev/attestation/publication/v10
          predicate-path: dist/kristal-publication/attestation-predicate.json
'''
    return f'''name: Kristal Publish State

on:
  workflow_dispatch:
    inputs:
      state_file:
        description: Repository-relative path to a v9 state snapshot (for example kristals/<slug>/state/state-snapshot.json)
        required: true

permissions:
  contents: write
{attest_permissions}
jobs:
  publish:
    runs-on: ubuntu-latest
{environment_line}    env:
      STATE_FILE: ${{{{ inputs.state_file }}}}
    steps:
      - uses: {ACTION_CHECKOUT}
        with:
          ref: ${{{{ github.sha }}}}
      - uses: {ACTION_SETUP_NODE}
        with:
          node-version: '22'
          package-manager-cache: false
      - name: Load pinned Kristal framework
        uses: {ACTION_CHECKOUT}
        with:
          repository: {fw}
          ref: {ref}
          path: .kristal-framework
      - name: Validate state path
        shell: bash
        run: |
          set -euo pipefail
          python - <<'PYSAFE'
          import os, pathlib
          root=pathlib.Path(os.environ['GITHUB_WORKSPACE']).resolve()
          raw=os.environ['STATE_FILE']
          p=(root/raw).resolve(strict=True)
          if root != p and root not in p.parents: raise SystemExit('state_file escapes GITHUB_WORKSPACE')
          if p.is_symlink(): raise SystemExit('state_file must not be a symlink')
          print(p)
          PYSAFE
      - name: Validate hosted read surface when present
        shell: bash
        run: |
          set -euo pipefail
          SURFACE_ROOT=$(dirname "$(dirname "$STATE_FILE")")
          if [ -f "$SURFACE_ROOT/.kristal/sync-manifest.json" ] && [ -f ".kristal/tools/validate-read-surface.py" ]; then
            python .kristal/tools/validate-read-surface.py validate-root \
              --repo . \
              --root "$SURFACE_ROOT" \
              --framework-cli .kristal-framework/reference/js/bin/kristal-ref.mjs
          else
            echo "No hosted read-surface manifest for $STATE_FILE; using state-only compatibility validation."
          fi
      - name: Build and verify publication bundle
        shell: bash
        run: |
          set -euo pipefail
          node .kristal-framework/reference/js/bin/kristal-ref.mjs verify-state-v9 "$STATE_FILE"
          rm -rf dist/kristal-publication
          node .kristal-framework/reference/js/bin/kristal-ref.mjs build-publication-bundle-v10 "$STATE_FILE" .kristal/node.json .kristal/bindings/github.json dist/kristal-publication --source-commit "$GITHUB_SHA"
          node .kristal-framework/reference/js/bin/kristal-ref.mjs verify-publication-bundle-v10 dist/kristal-publication
          PUB_ID=$(jq -r .publication_id dist/kristal-publication/publication.json)
          TAG="kristal-pub-${{PUB_ID##*:}}"
          echo "TAG=$TAG" >> "$GITHUB_ENV"
          jq -n --arg publication_id "$PUB_ID" --arg source_commit "$GITHUB_SHA" --arg framework_commit "{ref}" '{{publication_id:$publication_id,source_commit:$source_commit,framework_commit:$framework_commit}}' > dist/kristal-publication/attestation-predicate.json
{attest_step}      - name: Create or verify immutable publication release
        env:
          GH_TOKEN: ${{{{ github.token }}}}
        shell: bash
        run: |
          set -euo pipefail
          TMP=$(mktemp -d)
          trap 'rm -rf "$TMP"' EXIT
          if gh release view "$TAG" --json tagName >/dev/null 2>&1; then
            gh release download "$TAG" --dir "$TMP"
            node .kristal-framework/reference/js/bin/kristal-ref.mjs verify-publication-bundle-v10 "$TMP"
            cmp dist/kristal-publication/publication.json "$TMP/publication.json"
            echo "Publication $TAG already exists and is identical."
            exit 0
          fi
          gh release create "$TAG" --draft --target "$GITHUB_SHA" --title "$TAG" --notes "Kristal v10 publication from $GITHUB_SHA"
          gh release upload "$TAG" dist/kristal-publication/state-snapshot.json dist/kristal-publication/bundle-manifest.json dist/kristal-publication/publication.json --clobber=false
          gh release download "$TAG" --dir "$TMP"
          node .kristal-framework/reference/js/bin/kristal-ref.mjs verify-publication-bundle-v10 "$TMP"
          cmp dist/kristal-publication/publication.json "$TMP/publication.json"
          gh release edit "$TAG" --draft=false
'''


def repo_readme(spec: RepoSpec, hub: str) -> str:
    hub_line = f"- Administrative directory: `{hub}`\n" if spec.visibility != "public" else ""
    collection_line = "- AI/GitHub discovery index: `kristals/index.json`\n" if spec.role == "collection" else ""
    return f'''# {spec.name}\n\nKristal v10 node.\n\n- Node: `{spec.node_id}`\n- Role: `{spec.role}`\n- Visibility: `{spec.visibility}`\n{hub_line}- Semantic state baseline: `kristal.state/9.0`\n- Host profile: `kristal.host/github/1.0`\n{collection_line}\nThe `.kristal/` directory is operational metadata. Logical commitments remain independent of GitHub hosting.\n'''


def global_profile(owner: str, hub: str) -> str:
    return '''# Kristal network\n\nThis GitHub account exposes public Kristal v10 nodes.\n\n- Standard: `Kristal 10.0`\n- Semantic-state baseline: `Kristal v9`\n\nPrivate administrative topology is intentionally not disclosed by this public profile.\n'''


def workflow_template(cfg: dict[str, Any]) -> tuple[str, str]:
    body=qualify_workflow(cfg); props=json.dumps({"name":"Kristal v10 qualification","description":"Validate a Kristal v10 node and GitHub host binding.","iconName":"octicon verified","categories":["Continuous integration"]},indent=2)+"\n"; return body,props


def ensure_repo(client: GhClient, cfg: dict[str, Any], spec: RepoSpec) -> dict[str, Any]:
    owner=cfg["account"]["owner"]; current=client.repo(owner,spec.name)
    if current:
        actual=current.get("visibility") if isinstance(current,dict) else None
        if actual is None and isinstance(current,dict) and "private" in current: actual="private" if current.get("private") else "public"
        if actual and actual!=spec.visibility: raise BootstrapError(f"repository {owner}/{spec.name} exists with visibility {actual}, expected {spec.visibility}")
        return {"status":"exists","repo":current}
    return {"status":"created","repo":client.create_repo(owner,cfg["account"]["kind"],spec)}


def effective_branch(client: GhClient, cfg: dict[str, Any], repo: str) -> str:
    current=client.repo(cfg["account"]["owner"],repo)
    if isinstance(current,dict) and current.get("default_branch"): return current["default_branch"]
    return cfg.get("policy",{}).get("default_branch","main")


def _hash_text(s: str) -> str: return hashlib.sha256(s.encode()).hexdigest()

def _load_json_file(client: GhClient, owner: str, repo: str, path: str, default: Any) -> Any:
    got=client.get_text_file(owner,repo,path)
    if not got: return default
    try: return json.loads(got[0])
    except Exception: raise BootstrapError(f"managed JSON {owner}/{repo}/{path} is malformed")


def _apply_managed_file(client: GhClient, owner: str, repo: str, branch: str, path: str, desired: str, ledger: dict[str, str], adopt: bool=False) -> str:
    got=client.get_text_file(owner,repo,path)
    desired_hash=_hash_text(desired)
    if not got:
        client.put_text_file(owner,repo,path,desired,f"Configure Kristal v10: {path}",branch,overwrite_managed=True); ledger[path]=desired_hash; return "created"
    current,_=got; current_hash=_hash_text(current)
    if current_hash==desired_hash: ledger[path]=desired_hash; return "unchanged"
    previous=ledger.get(path)
    if previous==current_hash or adopt:
        client.put_text_file(owner,repo,path,desired,f"Update managed Kristal file: {path}",branch,overwrite_managed=True); ledger[path]=desired_hash; return "updated"
    raise BootstrapError(f"managed file conflict at {owner}/{repo}/{path}: current content was modified outside bootstrap; use explicit adoption/repair")


def _registry_entries(client: GhClient, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    owner=cfg["account"]["owner"]; hub=cfg["hub"]["repository"]
    doc=_load_json_file(client,owner,hub,".kristal/network-registry.json",{"nodes":[]})
    return doc.get("nodes",[]) if isinstance(doc,dict) and isinstance(doc.get("nodes",[]),list) else []


def seed_node_repo(client: GhClient, cfg: dict[str, Any], spec: RepoSpec, is_hub: bool=False, adopt: bool=False, effective: dict[str,str] | None=None, all_specs: list[RepoSpec] | None=None) -> list[tuple[str,str]]:
    owner=cfg["account"]["owner"]; branch=effective_branch(client,cfg,spec.name); hub=cfg["hub"]["repository"]; effective=effective or {}
    state=_load_json_file(client,owner,spec.name,".kristal/bootstrap-state.json",{"managed_files":{}}); ledger=dict(state.get("managed_files",{})) if isinstance(state,dict) else {}
    files={
        ".kristal/node.json":json.dumps(node_manifest(spec,directory=is_hub),indent=2)+"\n",
        ".kristal/bindings/github.json":json.dumps(github_binding(owner,cfg['account']['kind'],spec,branch,effective),indent=2)+"\n",
        ".kristal/capabilities.json":json.dumps(capabilities_doc(effective),indent=2)+"\n",
        ".github/workflows/kristal-qualify.yml":qualify_workflow(cfg,include_directory=is_hub or spec.role=="directory"),
        ".github/workflows/kristal-publish.yml":publish_workflow(cfg,cfg.get('features',{}).get('attestations','best_effort')),
    }
    if spec.role == "collection":
        files[".kristal/tools/validate-read-surface.py"] = collection_validator_script()
        files[".github/workflows/kristal-ingest.yml"] = collection_ingest_workflow(cfg)
    if is_hub:
        registry=_registry_entries(client,cfg)
        files[".kristal/directory.json"]=json.dumps(directory_doc(cfg,all_specs or desired_repos(cfg),registry),indent=2)+"\n"
        if client.get_text_file(owner,spec.name,".kristal/network-registry.json") is None:
            client.put_text_file(owner,spec.name,".kristal/network-registry.json",json.dumps({"schema_version":"1.0","artifact_type":"kristal_network_registry","nodes":[]},indent=2)+"\n","Initialize Kristal network registry",branch,overwrite_managed=True)
    elif spec.role=="directory":
        files[".kristal/directory.json"]=json.dumps({"schema_version":"10.0","artifact_type":"kristal_directory","directory_id":f"urn:kristal:directory:{hashlib.sha256(spec.node_id.encode()).hexdigest()[:24]}","node_id":spec.node_id,"entries":[]},indent=2)+"\n"
    results=[]
    for path_,content in files.items(): results.append((path_,_apply_managed_file(client,owner,spec.name,branch,path_,content,ledger,adopt)))
    # README is create-only: never overwrite user documentation.
    if client.get_text_file(owner,spec.name,"README.md") is None:
        client.put_text_file(owner,spec.name,"README.md",repo_readme(spec,hub),"Initialize Kristal node README",branch,overwrite_managed=True); results.append(("README.md","created"))
    ledger_doc={"schema_version":"1.0","artifact_type":"kristal_bootstrap_state","bootstrap_version":BOOTSTRAP_VERSION,"node_id":spec.node_id,"managed_files":ledger}
    ledger_text=json.dumps(ledger_doc,indent=2)+"\n"; got=client.get_text_file(owner,spec.name,".kristal/bootstrap-state.json")
    if not got or got[0]!=ledger_text: client.put_text_file(owner,spec.name,".kristal/bootstrap-state.json",ledger_text,"Update Kristal bootstrap state",branch,overwrite_managed=True); results.append((".kristal/bootstrap-state.json","updated" if got else "created"))
    else: results.append((".kristal/bootstrap-state.json","unchanged"))
    return results


def seed_global(client: GhClient,cfg: dict[str,Any],specs: list[RepoSpec],adopt: bool=False)->list[tuple[str,str,str]]:
    owner=cfg['account']['owner']; hub=cfg['hub']['repository']; out=[]; gh_spec=next((s for s in specs if s.name=='.github'),None)
    if gh_spec:
        wf,props=workflow_template(cfg); files={'profile/README.md':global_profile(owner,hub),'workflow-templates/kristal-node.yml':wf,'workflow-templates/kristal-node.properties.json':props}
        for path_,content in files.items():
            got=client.get_text_file(owner,gh_spec.name,path_)
            if not got: status=client.put_text_file(owner,gh_spec.name,path_,content,f'Configure global Kristal integration: {path_}',effective_branch(client,cfg,gh_spec.name),overwrite_managed=True)
            elif got[0]==content: status='unchanged'
            else: status='kept'
            out.append((gh_spec.name,path_,status))
    if cfg['account']['kind']=='organization':
        priv=next((s for s in specs if s.name=='.github-private'),None)
        if priv:
            text=f'# Internal Kristal network\n\nAdministrative root directory: `{owner}/{hub}`.\n'; got=client.get_text_file(owner,priv.name,'profile/README.md'); status='unchanged' if got and got[0]==text else ('kept' if got else client.put_text_file(owner,priv.name,'profile/README.md',text,'Configure internal Kristal profile',effective_branch(client,cfg,priv.name),overwrite_managed=True)); out.append((priv.name,'profile/README.md',status))
    return out


def set_repo_topics(client: GhClient, owner: str, spec: RepoSpec) -> str:
    desired={'kristal','kristal-v10'} | ({f'kristal-{spec.role}'} if spec.role in {'collection','directory','gateway'} else set())
    current=client.api('GET',f'/repos/{owner}/{spec.name}/topics',optional=True) or {}; names=set(current.get('names',[])) if isinstance(current,dict) else set(); merged=sorted(names|desired)
    if merged==sorted(names): return 'unchanged'
    client.api('PUT',f'/repos/{owner}/{spec.name}/topics',{'names':merged}); return 'updated'


def enable_immutable_releases(client: GhClient, owner: str, spec: RepoSpec, mode: str) -> str:
    if mode=='off' or spec.role not in {'collection','directory','publisher','gateway'}: return 'skipped'
    try:
        current=client.api('GET',f'/repos/{owner}/{spec.name}/immutable-releases',optional=True)
        if isinstance(current,dict) and current.get('enabled') is True: return 'present'
        client.api('PUT',f'/repos/{owner}/{spec.name}/immutable-releases'); return 'enabled'
    except BootstrapError:
        if mode=='required': raise
        return 'unavailable'


def ensure_environment(client: GhClient, owner: str, spec: RepoSpec, mode: str) -> str:
    if mode=='off' or spec.role not in {'collection','directory','publisher','gateway'}: return 'skipped'
    try:
        current=client.api('GET',f'/repos/{owner}/{spec.name}/environments/production',optional=True)
        if current: return 'present'
        client.api('PUT',f'/repos/{owner}/{spec.name}/environments/production',{}); return 'created'
    except BootstrapError:
        if mode=='required': raise
        return 'unavailable'


def configure_org_custom_properties(client: GhClient,cfg: dict[str,Any],specs: list[RepoSpec],mode: str)->str:
    if cfg['account']['kind']!='organization' or mode=='off': return 'skipped'
    owner=cfg['account']['owner']; schema={"properties":[{"property_name":"kristal_standard","value_type":"single_select","required":False,"allowed_values":["10.0"],"values_editable_by":"org_actors"},{"property_name":"kristal_role","value_type":"single_select","required":False,"allowed_values":["global","global-private","profile","directory","collection","gateway","publisher"],"values_editable_by":"org_actors"},{"property_name":"kristal_visibility","value_type":"single_select","required":False,"allowed_values":["public","private","internal"],"values_editable_by":"org_actors"}]}
    try:
        client.api('PATCH',f'/orgs/{owner}/properties/schema',schema)
        for s in specs: client.api('PATCH',f'/repos/{owner}/{s.name}/properties/values',{"properties":[{"property_name":"kristal_standard","value":"10.0"},{"property_name":"kristal_role","value":s.role},{"property_name":"kristal_visibility","value":s.visibility}]})
        return 'configured'
    except BootstrapError:
        if mode=='required': raise
        return 'unavailable'


def observed_fingerprint(client: GhClient,cfg: dict[str,Any])->str:
    owner=cfg['account']['owner']; rows=[]
    for s in desired_repos(cfg):
        r=client.repo(owner,s.name); rows.append([s.name,(r or {}).get('id'),(r or {}).get('visibility'),(r or {}).get('default_branch')])
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def plan_account(client: GhClient,cfg: dict[str,Any])->dict[str,Any]:
    owner=cfg['account']['owner']; account=account_preflight(client,cfg,required=False); fw=framework_preflight(client,cfg,required=False); actions=[]
    actions.append({"action":"verify","target":"account","status":account['status']})
    fw_action = {"action":"verify","target":fw['repository'],"feature":"framework","status":fw['status'],"ref":fw.get("ref"),"visibility":fw.get("visibility"),"ref_resolved":fw.get("ref_resolved"),"reason":fw.get("reason")}
    if fw.get("verification_attempts"):
        fw_action["verification_attempts"] = fw["verification_attempts"]
    actions.append(fw_action)
    for spec in desired_repos(cfg):
        r=client.repo(owner,spec.name); actions.append({"action":"reuse" if r else "create","repository":f"{owner}/{spec.name}","visibility":spec.visibility,"role":spec.role})
    return {"config_fingerprint":config_fingerprint(cfg),"observed_fingerprint":observed_fingerprint(client,cfg),"actions":actions}


def _effective_features(client: GhClient,cfg: dict[str,Any],spec: RepoSpec)->dict[str,str]:
    owner=cfg['account']['owner']; imm=enable_immutable_releases(client,owner,spec,cfg.get('features',{}).get('immutable_releases','best_effort')); env=ensure_environment(client,owner,spec,cfg.get('features',{}).get('environments','best_effort')); att_mode=cfg.get('features',{}).get('attestations','best_effort')
    return {"immutable_releases":imm,"environment":env,"attestations":"required" if att_mode=='required' else ("configured" if att_mode=='best_effort' else "off")}


def apply_account(client: GhClient,cfg: dict[str,Any],overwrite: bool=False,expected_observed_fingerprint: str|None=None)->dict[str,Any]:
    account_preflight(client,cfg,required=True); framework_preflight(client,cfg,required=True)
    if expected_observed_fingerprint and observed_fingerprint(client,cfg)!=expected_observed_fingerprint: raise BootstrapError('plan is stale: observed GitHub state changed; recalculate plan')
    owner=cfg['account']['owner']; specs=desired_repos(cfg); report={"repositories":{},"global_files":[],"features":{},"warnings":[]}
    for spec in specs: report['repositories'][spec.name]=ensure_repo(client,cfg,spec)['status']
    specs=hydrate_existing_node_ids(client,cfg,specs)
    report['global_files']=seed_global(client,cfg,specs,overwrite); hub_name=cfg['hub']['repository']
    for spec in specs:
        if spec.role in {'collection','directory','gateway','publisher'}:
            eff=_effective_features(client,cfg,spec); files=seed_node_repo(client,cfg,spec,is_hub=(spec.name==hub_name),adopt=overwrite,effective=eff,all_specs=specs)
            report['repositories'][spec.name]={"repo":report['repositories'][spec.name],"files":files,"features":eff,"topics":set_repo_topics(client,owner,spec)}
    report['features']['custom_properties']=configure_org_custom_properties(client,cfg,specs,cfg.get('features',{}).get('custom_properties','best_effort'))
    return report


def _registry_doc(client: GhClient,cfg: dict[str,Any])->tuple[dict[str,Any],str]:
    owner=cfg['account']['owner']; hub=cfg['hub']['repository']; got=client.get_text_file(owner,hub,'.kristal/network-registry.json')
    if not got: raise BootstrapError('hub network registry missing; run account apply first')
    try: return json.loads(got[0]),got[1]
    except Exception: raise BootstrapError('hub network registry is malformed')


def register_repo_in_hub(client: GhClient,cfg: dict[str,Any],spec: RepoSpec)->str:
    owner=cfg['account']['owner']; hub=cfg['hub']['repository']; branch=effective_branch(client,cfg,hub); doc,sha=_registry_doc(client,cfg)
    nodes=[e for e in doc.get('nodes',[]) if e.get('node_id')!=spec.node_id and e.get('metadata',{}).get('repository')!=spec.name]
    nodes.append(_directory_entry(owner,spec)); nodes.sort(key=lambda e:e['node_id']); doc['nodes']=nodes
    body={"message":f"Register Kristal node {spec.name}","content":base64.b64encode((json.dumps(doc,indent=2)+'\n').encode()).decode(),"sha":sha,"branch":branch}; client.api('PUT',f'/repos/{owner}/{hub}/contents/.kristal/network-registry.json',body)
    specs=hydrate_existing_node_ids(client,cfg,desired_repos(cfg)); directory=directory_doc(cfg,specs,nodes); current=client.get_text_file(owner,hub,'.kristal/directory.json'); body2={"message":f"Project Kristal directory after registering {spec.name}","content":base64.b64encode((json.dumps(directory,indent=2)+'\n').encode()).decode(),"branch":branch};
    if current: body2['sha']=current[1]
    client.api('PUT',f'/repos/{owner}/{hub}/contents/.kristal/directory.json',body2); return 'registered'


def apply_single_repo(client: GhClient,cfg: dict[str,Any],name: str,visibility: str,role: str='collection',collection: str|None=None,register: bool=True,overwrite: bool=False)->dict[str,Any]:
    account_preflight(client,cfg,required=True); framework_preflight(client,cfg,required=True)
    if visibility=='internal' and cfg['account']['kind']!='organization': raise BootstrapError('internal visibility requires organization account')
    owner=cfg['account']['owner']; existing=client.repo(owner,name); existing_id=_existing_node_id(client,owner,name) if existing else None
    if not existing_id:
        try:
            reg=_registry_entries(client,cfg); existing_id=next((e['node_id'] for e in reg if e.get('metadata',{}).get('repository')==name),None)
        except Exception: existing_id=None
    nid=existing_id or f"urn:uuid:{uuid.uuid4()}"; spec=RepoSpec(name,visibility,role,nid,f'Kristal {role}: {name}',collection or name,identity_key=nid)
    status=ensure_repo(client,cfg,spec)['status']; eff=_effective_features(client,cfg,spec); files=seed_node_repo(client,cfg,spec,is_hub=False,adopt=overwrite,effective=eff); topics=set_repo_topics(client,owner,spec); registered=register_repo_in_hub(client,cfg,spec) if register else 'skipped'
    return {'repository':status,'node_id':nid,'files':files,'features':eff,'topics':topics,'hub':registered}


def config_fingerprint(cfg: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(cfg,sort_keys=True,separators=(',',':')).encode()).hexdigest()
