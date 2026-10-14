#!/usr/bin/env python3
"""Full-inventory corroboration of PR1864's selected-manifest commitment gap.
All mutations are private temporary copies; selected files remain byte-for-byte unchanged.
Prepared for woklerx with OpenAI Codex assistance. Apache-2.0.
"""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util, json, shutil, tempfile, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECORD_SHA = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
TARGET = "research/complex-sw4-frame8/code/assemble.py"


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def check_input_pins():
    for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] == "input":
            need(
                sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "pinned input drift: " + row["path"],
            )


def main():
    check_input_pins()
    record_raw = (ROOT / "certificates/selected-result.json").read_bytes()
    need(sha256(record_raw).hexdigest() == RECORD_SHA, "selected record drift")
    record = json.loads(record_raw)
    manifest_name = record["source_manifest"]
    manifest_raw = (ROOT / manifest_name).read_bytes()
    manifest = json.loads(manifest_raw)
    need(
        TARGET in manifest["files"] and TARGET not in record["proof_supplements"],
        "mutation source boundary changed",
    )
    spec = importlib.util.spec_from_file_location(
        "production_selected_checker", ROOT / "scripts/verify_selected_result.py"
    )
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    sources = (
        set(manifest["files"])
        | set(record["proof_supplements"])
        | {
            record[k]
            for k in ["certificate", "source_manifest", "proof", "review", "validation"]
        }
    )
    before = {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in sources}
    cases = []
    with tempfile.TemporaryDirectory(prefix="selected-inventory-audit-") as temp:
        root = Path(temp).resolve()
        need(
            root.is_relative_to(Path(tempfile.gettempdir()).resolve()),
            "temporary copy containment",
        )
        for p in sources:
            dst = root / p
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / p, dst)

        def run(label, rec, want, error=None):
            try:
                checker.check(rec, root)
                status = "accepted"
                message = None
            except ValueError as exc:
                status = "rejected"
                message = str(exc)
            need(status == want, label + ": " + status)
            if error:
                need(error in message, label + " wrong error")
            cases.append({"case": label, "status": status, "error": message})

        run("all original 1579 inventory files", record, "accepted")
        original = (root / TARGET).read_bytes()
        bad = b'raise SystemExit("intentional audit-only semantic corruption")\n'
        (root / TARGET).write_bytes(bad)
        run(
            "source changed without updating manifest",
            record,
            "rejected",
            "inventory or bytes changed",
        )
        forged = deepcopy(manifest)
        forged["files"][TARGET] = sha256(bad).hexdigest()
        (root / manifest_name).write_text(
            json.dumps(forged, indent=2) + "\n", encoding="utf-8"
        )
        run(
            "source and inventory coherently changed; record unchanged",
            record,
            "accepted",
        )
        # Demonstrate a concrete repair using the EXISTING proof_supplements mechanism.
        # This is a private in-memory hypothetical record, never the live selection.
        anchored = deepcopy(record)
        anchored["proof_supplements"][manifest_name] = sha256(manifest_raw).hexdigest()
        run(
            "hypothetical existing supplement anchor rejects coherent rewrite",
            anchored,
            "rejected",
            "proof supplement changed",
        )
        (root / TARGET).write_bytes(original)
        (root / manifest_name).write_bytes(manifest_raw)
        run(
            "hypothetical supplement anchor accepts original snapshot",
            anchored,
            "accepted",
        )
        cert_path = root / record["certificate"]
        cert_raw = cert_path.read_bytes()
        cert_path.write_bytes(cert_raw + b"\n")
        run(
            "certificate bytes changed", record, "rejected", "certificate bytes changed"
        )
        cert_path.write_bytes(cert_raw)
        proof_name = record["proof"]
        proof_path = root / proof_name
        proof_raw = proof_path.read_bytes()
        proof_path.write_bytes(proof_raw + b"\n")
        run(
            "primary proof bytes changed",
            record,
            "rejected",
            "proof supplement changed",
        )
        proof_path.write_bytes(proof_raw)
    after = {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in sources}
    need(before == after, "live source changed")
    out = {
        "status": "PASS_FULL_SELECTED_MANIFEST_AUDIT",
        "source_pr": 1864,
        "source_head": "3d54b62bee5e7e2027aaffd9a30c31adc3b84c0a",
        "inventory_files": len(manifest["files"]),
        "package_roots": len(manifest["package_roots"]),
        "copied_files": len(sources),
        "copied_bytes": sum((ROOT / p).stat().st_size for p in sources),
        "selected_record_sha256": RECORD_SHA,
        "manifest_sha256": sha256(manifest_raw).hexdigest(),
        "mutation_target": TARGET,
        "cases": cases,
        "live_source_hashes_unchanged": True,
        "added_evidence": "The real selected 1579-file inventory reproduces the predecessor minimal fixture. An existing proof_supplements entry anchors the manifest without a new verifier field; demonstrated only on a private hypothetical record.",
        "limits": "Fast integrity check only. No cold replay, theorem audit, attacker model, selected record change or claim of corruption in actual selected files.",
    }
    target = HERE / "RESULT.json"
    if "--write" in sys.argv:
        target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    else:
        need(json.loads(target.read_bytes()) == out, "receipt mismatch")
    print(
        out["status"],
        f"files={len(manifest['files'])} roots=13 cases={len(cases)} live_unchanged=True",
    )


if __name__ == "__main__":
    main()
