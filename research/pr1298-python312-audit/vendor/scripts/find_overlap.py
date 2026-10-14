#!/usr/bin/env python3
"""Search PR bodies, discussion claims and local package READMEs for possible overlap.

Standard library + optional authenticated gh CLI. Remote snapshots live outside
the checkout. Results are leads, not a novelty certificate. Douglas Colkitt,
with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = "CrocSwap/integer-mult-bounds"


def now():
    return datetime.now(timezone.utc).isoformat()


def gh_json(args, payload=None):
    result = subprocess.run(
        ["gh", "api", *args], input=None if payload is None else json.dumps(payload),
        text=True, encoding="utf-8", capture_output=True, timeout=90, check=True,
    )
    value = json.loads(result.stdout)
    if isinstance(value, dict) and value.get("errors"):
        raise ValueError("GitHub GraphQL errors: " + json.dumps(value["errors"]))
    return value


def graphql(query, variables):
    return gh_json(["graphql", "--input", "-"], {"query": query, "variables": variables})["data"]


def pull_records(pages):
    return [{"kind": "pr", "number": pr["number"], "title": pr["title"],
             "body": pr.get("body") or "", "url": pr["html_url"],
             "head": pr["head"]["sha"], "updated_at": pr["updated_at"],
             "draft": pr.get("draft", False), "state": pr["state"]}
            for page in pages for pr in page]


def fetch_discussions():
    records = []
    cursor = None
    while True:
        result = graphql('''query($cursor:String) {
          repository(owner:"CrocSwap",name:"integer-mult-bounds") {
            discussions(first:50,after:$cursor) {
              pageInfo {hasNextPage endCursor}
              nodes {id number title body url updatedAt}
            }
          }
        }''', {"cursor": cursor})["repository"]["discussions"]
        for discussion in result["nodes"]:
            common = {"number": discussion["number"], "title": discussion["title"]}
            records.append({**common, "kind": "discussion", "body": discussion["body"],
                            "url": discussion["url"], "updated_at": discussion["updatedAt"]})
            comment_cursor = None
            while True:
                connection = graphql('''query($id:ID!, $cursor:String) {
                  node(id:$id) { ... on Discussion {
                    comments(first:100,after:$cursor) {
                      pageInfo {hasNextPage endCursor}
                      nodes {id body url updatedAt replies(first:100) {
                        pageInfo {hasNextPage endCursor} nodes {body url updatedAt}
                      }}
                    }
                  }}
                }''', {"id": discussion["id"], "cursor": comment_cursor})["node"]["comments"]
                for comment in connection["nodes"]:
                    records.append({**common, "kind": "discussion-comment", "body": comment["body"],
                                    "url": comment["url"], "updated_at": comment["updatedAt"]})
                    replies = comment["replies"]
                    while True:
                        for reply in replies["nodes"]:
                            records.append({**common, "kind": "discussion-reply", "body": reply["body"],
                                            "url": reply["url"], "updated_at": reply["updatedAt"]})
                        if not replies["pageInfo"]["hasNextPage"]:
                            break
                        replies = graphql('''query($id:ID!, $cursor:String) {
                          node(id:$id) { ... on DiscussionComment {
                            replies(first:100,after:$cursor) {
                              pageInfo {hasNextPage endCursor} nodes {body url updatedAt}
                            }
                          }}
                        }''', {"id": comment["id"], "cursor": replies["pageInfo"]["endCursor"]})["node"]["replies"]
                if not connection["pageInfo"]["hasNextPage"]:
                    break
                comment_cursor = connection["pageInfo"]["endCursor"]
        if not result["pageInfo"]["hasNextPage"]:
            return records
        cursor = result["pageInfo"]["endCursor"]


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as out:
        tmp = Path(out.name)
        json.dump(data, out)
        out.write("\n")
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def error_summary(exc):
    if isinstance(exc, subprocess.CalledProcessError):
        return (exc.stderr or str(exc))[:700]
    return str(exc)[:700]


def remote_snapshot(cache, offline=False, refresh=False, max_age=300):
    warnings = []
    try:
        snapshot = json.loads(cache.read_text(encoding="utf-8"))
        if snapshot.get("schema_version") != 1 or snapshot.get("repository") != REPO:
            raise ValueError("cache schema or repository mismatch")
    except (OSError, ValueError):
        snapshot = {"schema_version": 1, "repository": REPO, "sources": {}}
    sources = snapshot.setdefault("sources", {})
    for name, fetch in (
        ("open_prs", lambda: pull_records(gh_json([
            "--paginate", "--slurp", f"repos/{REPO}/pulls?state=open&per_page=100&sort=updated&direction=desc"]))),
        ("discussions", fetch_discussions),
    ):
        cached = sources.get(name)
        age = None
        if cached:
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached["fetched_at"])).total_seconds()
            except (KeyError, ValueError, TypeError):
                cached = None
        fresh = cached is not None and age is not None and 0 <= age <= max_age
        if offline:
            warnings.append(f"{name}: offline; cached data may miss current changes")
        elif refresh or not fresh:
            try:
                # Replace each source only after every page succeeds.
                records = fetch()
                sources[name] = {"fetched_at": now(), "records": records, "complete_pagination": True}
                atomic_json(cache, snapshot)
                cached = sources[name]
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
                warnings.append(f"{name}: refresh failed; using old data if available: {error_summary(exc)}")
        if not cached:
            warnings.append(f"{name}: no usable remote snapshot")
            sources.pop(name, None)
    return snapshot, warnings


def local_records(root):
    records = []
    # Deliberately avoid vendored trees and large binary artifacts.
    paths = sorted([*(root / "research").glob("*/README.md"), *(root / "research").glob("*/TASK.json")])
    ledger = root / "docs/research/pr-ledger.md"
    if ledger.is_file():
        paths.append(ledger)
    for path in paths:
        if path.is_symlink():
            continue
        data = path.read_bytes()
        body = data.decode("utf-8", errors="replace")
        name = path.relative_to(root).as_posix()
        kind = {"README.md": "local-readme", "TASK.json": "local-task"}.get(path.name, "local-ledger")
        records.append({"kind": kind,
                        "title": name, "path": name, "body": body,
                        "sha256": hashlib.sha256(data).hexdigest()})
    return records


def search(records, terms, all_terms=False):
    terms = list(dict.fromkeys(t.strip().lower() for t in terms if t.strip()))
    if not terms:
        raise ValueError("provide at least one nonempty search term")
    matches = []
    for record in records:
        title, body = record["title"].lower(), record.get("body", "").lower()
        found = [term for term in terms if term in title or term in body]
        if not found or (all_terms and len(found) != len(terms)):
            continue
        positions = [body.find(term) for term in found if term in body]
        start = max(0, min(positions) - 100) if positions else 0
        matches.append({**{k: v for k, v in record.items() if k != "body"},
                        "matched_terms": found,
                        "score": sum(3 if t in title else 1 for t in found),
                        "excerpt": record.get("body", "")[start:start + 500]})
    return sorted(matches, key=lambda r: (-r["score"], r["kind"], r["title"], r.get("url", "")))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("terms", nargs="*", help="literal case-insensitive terms; quote multiword phrases")
    ap.add_argument("--task", help="add the named catalogue card's overlap terms")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--max-age", type=int, default=300, help="remote cache lifetime in seconds")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--all-terms", action="store_true")
    ap.add_argument("--json", action="store_true", dest="json_output")
    ap.add_argument("--cache", type=Path, default=Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "integer-mult-bounds/overlap.json")
    args = ap.parse_args()
    if args.max_age < 0 or args.limit < 1 or (args.offline and args.refresh):
        ap.error("use nonnegative max-age, positive limit, and either offline or refresh")
    if args.cache.resolve().is_relative_to(ROOT.resolve()):
        ap.error("keep the cache outside the repository")
    terms = list(args.terms)
    if args.task:
        catalog = json.loads((ROOT / "docs/research/agent-task-catalog.json").read_text(encoding="utf-8"))
        cards = [t for tr in catalog["tracks"] for t in tr["tasks"] if t["id"] == args.task]
        if not cards:
            ap.error("unknown task")
        terms.extend([args.task, *cards[0].get("overlap_terms", [])])
        terms.extend(Path(p).parent.name for p in cards[0]["starting_points"] if p.startswith("research/"))
    if not any(t.strip() for t in terms):
        ap.error("provide terms or --task")
    local = local_records(ROOT)
    snapshot, warnings = remote_snapshot(args.cache, args.offline, args.refresh, args.max_age)
    records = list(local)
    coverage = {}
    for name in ("open_prs", "discussions"):
        source = snapshot["sources"].get(name)
        coverage[name] = {k: source[k] for k in ("fetched_at", "complete_pagination")} if source else None
        if source:
            records.extend(source["records"])
            coverage[name]["records"] = len(source["records"])
    matches = search(records, terms, args.all_terms)
    report = {"status": "POSSIBLE_OVERLAP_NOT_A_NOVELTY_CERTIFICATE", "searched_at": now(),
              "terms": terms, "coverage": coverage, "local_records": len(local), "warnings": warnings,
              "limits": "Remote PR scope is open PRs including drafts. Closed work is searched through local READMEs, TASK metadata and ledger only. No code diffs or arbitrary package files are searched. Recheck relevant heads before submission.",
              "matches_total": len(matches), "matches": matches[:args.limit]}
    if args.json_output:
        print(json.dumps(report, indent=2))
    else:
        # Excerpts quote arbitrary UTF-8; a cp1252 pipe must escape them, not crash.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="backslashreplace")
        print(report["status"])
        print("Coverage: " + json.dumps(coverage))
        print(report["limits"])
        for warning in warnings:
            print("WARNING: " + warning)
        print(f"{len(matches)} possible matches; showing {min(args.limit, len(matches))}")
        for match in matches[:args.limit]:
            print(f"\n[{match['kind']}] {match['title']}\n{match.get('url', match.get('path'))}")
            if match.get("head"):
                print("Head: " + match["head"])
            print(match["excerpt"])


if __name__ == "__main__":
    main()
