#!/usr/bin/env python3
"""Read-only, reproducible research suggestions; never a reservation service.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("docs/research/agent-task-catalog.json")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def validate_catalog(catalog, root):
    if catalog.get("schema_version") != 1:
        raise ValueError("unsupported catalogue schema")
    revision = catalog.get("priority_revision")
    if type(revision) is not int or revision < 1:
        raise ValueError("priority_revision must be a positive integer")
    log = root / catalog["priority_log"]
    if not log.resolve().is_relative_to(root.resolve()) or not log.is_file():
        raise ValueError("missing or external priority log")
    tracks = catalog.get("tracks", [])
    if not tracks:
        raise ValueError("empty catalogue")
    ids = set()
    task_ids = set()
    for track in tracks:
        ident = track["id"]
        if ident in ids or not re.fullmatch(r"[a-z0-9-]+", ident):
            raise ValueError("duplicate or invalid track id")
        ids.add(ident)
        if type(track["weight"]) is not int or track["weight"] <= 0:
            raise ValueError("weights must be positive integers")
        if not track["tasks"]:
            raise ValueError("track has no tasks")
        for task in track["tasks"]:
            if task["id"] in task_ids:
                raise ValueError("duplicate task id")
            task_ids.add(task["id"])
            if not task["question"] or not task["acceptance_gate"] or not task["methods"]:
                raise ValueError("incomplete task card")
            if not task["starting_points"]:
                raise ValueError("task needs a starting point")
            for key in ("first_step", "first_experiment", "bottleneck_link", "allowed_variations", "scope_change_triggers", "overlap_terms"):
                if not task.get(key):
                    raise ValueError("missing actionable task field: " + key)
            step = task["first_step"]
            if not step.get("expected") or not step.get("inspect") or not step.get("command"):
                raise ValueError("incomplete first step")
            script = step["command"][-1]
            if not (root / script).is_file():
                raise ValueError("missing first-step script: " + script)
            for name in task["starting_points"]:
                path = root / name
                if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
                    raise ValueError(f"missing or external starting point: {name}")
    if sum(t["weight"] for t in tracks) != 100:
        raise ValueError("track weights must sum to 100")


def scope_key(task_id, method):
    # Base and nonce intentionally do not affect the semantic collision key.
    return digest(canonical({"task": task_id, "method": method}))[:20]


def select(catalog, seed, track_id=None, task_id=None):
    if not re.fullmatch(r"[0-9a-fA-F]{32}", seed):
        raise ValueError("seed must be exactly 32 hexadecimal digits")
    seed = seed.lower()

    def draw(label):
        return int(digest(canonical([seed, label])), 16)

    tracks = catalog["tracks"]
    if task_id:
        owners = [t for t in tracks if any(card["id"] == task_id for card in t["tasks"])]
        if len(owners) != 1 or (track_id and owners[0]["id"] != track_id):
            raise ValueError("unknown task or task/track mismatch")
        track_id = owners[0]["id"]
    if track_id is not None:
        matches = [t for t in tracks if t["id"] == track_id]
        if not matches:
            raise ValueError(f"unknown track: {track_id}")
        track = matches[0]
    else:
        ticket = draw("track") % 100
        for track in tracks:
            ticket -= track["weight"]
            if ticket < 0:
                break

    ordered = sorted([t for t in track["tasks"] if not task_id or t["id"] == task_id],
                     key=lambda t: draw("task:" + t["id"]))
    suggestions = []
    for task in ordered[:3]:
        method = task["methods"][draw("method:" + task["id"]) % len(task["methods"])]
        suggestions.append({
            "task_id": task["id"], "scope_key": scope_key(task["id"], method),
            "question": task["question"], "method": method,
            "starting_points": task["starting_points"],
            "acceptance_gate": task["acceptance_gate"],
            **{key: task[key] for key in ("first_step", "first_experiment", "bottleneck_link", "allowed_variations", "scope_change_triggers", "overlap_terms")},
            "scope_rule": "If you change the card's premise, record scope_status=changed and explain why. A package metadata check cannot establish mathematical relevance.",
        })
    return {"seed": seed, "track": track["id"], "suggestions": suggestions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", help="32 hex digits; default: fresh OS-random 128-bit nonce")
    parser.add_argument("--track", help="override weighted track selection; see catalogue")
    parser.add_argument("--task", help="show one specific card, without rerolling an existing assignment")
    args = parser.parse_args()
    try:
        catalog_bytes = (ROOT / CATALOG).read_bytes()
        catalog = json.loads(catalog_bytes)
        validate_catalog(catalog, ROOT)
        result = select(catalog, args.seed if args.seed is not None else secrets.token_hex(16), args.track, args.task)
        selected_bytes = (ROOT / "certificates/selected-result.json").read_bytes()
        selected = json.loads(selected_bytes)
        try:
            base = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                capture_output=True, text=True, encoding="utf-8",
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            base = None
        result.update({
            "base_commit": base,
            "catalog_assessed_on": catalog.get("assessed_on"),
            "priority_revision": catalog["priority_revision"],
            "priority_log": catalog["priority_log"],
            "catalog_sha256": digest(catalog_bytes),
            "selected_record_sha256": digest(selected_bytes),
            "selected": {k: selected[k] for k in ("kappa", "review", "source_manifest", "reproduce")},
            "status": "SUGGESTIONS_ONLY_NOT_RESERVED",
            "next_step": "Check live overlap, refine one question's object and domain, and record a bounded task card. A different seed or scope key is not evidence of novelty.",
        })
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
