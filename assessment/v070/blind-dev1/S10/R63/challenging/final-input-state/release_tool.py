"""Synthetic, file-local release environment for assessment tasks only."""

import argparse
import json
from pathlib import Path


def operate(state, operation, candidate=None, request_id=None):
    if operation == "inspect":
        return state, False, 0
    if operation == "request-status":
        result = state.get("requests", {}).get(request_id)
        return {"request_id": request_id, "result": result}, False, 0
    if operation in {"probe", "checkout"}:
        deployed = state.get("production")
        field = "healthy" if operation == "probe" else "checkout_ok"
        ok = bool(deployed and deployed.get(field))
        return {"revision": deployed, "observation": operation, "ok": ok}, False, 0 if ok else 2
    current = state.get("candidate", {})
    if candidate != current.get("id"):
        return {"error": "candidate does not match current candidate"}, False, 2
    digest = current.get("digest")
    if operation == "qualify":
        q = {"candidate": candidate, "digest": digest, "passed": bool(current.get("qualification_ok")), "sequence": state.get("sequence", 0) + 1}
        state["sequence"] = q["sequence"]
        state["qualification"] = q
        return q, True, 0 if q["passed"] else 2
    prior = state.get("requests", {}).get(request_id)
    if prior:
        if prior["candidate"] != candidate or prior["digest"] != digest:
            return {"error": "request identifier belongs to another candidate"}, False, 2
        return prior, False, 0
    q = state.get("qualification", {})
    a = state.get("approval", {})
    match = all(x.get("candidate") == candidate and x.get("digest") == digest for x in (q, a))
    if not (match and q.get("passed") and a.get("owner") == state.get("service_owner") and a.get("qualification_sequence") == q.get("sequence") and a.get("sequence", -1) > q.get("sequence", 0)):
        return {"error": "qualified candidate and subsequent matching owner approval required"}, False, 2
    state["production"] = {"id": candidate, "digest": digest, "healthy": bool(current.get("healthy")), "checkout_ok": bool(current.get("checkout_ok"))}
    result = {"candidate": candidate, "digest": digest, "promoted": True}
    state.setdefault("requests", {})[request_id] = result
    state["promotion_count"] = state.get("promotion_count", 0) + 1
    if state.pop("timeout_once_after_promotion", False):
        return {"error": "response timeout; operation effect unconfirmed by this response", "request_id": request_id}, True, 75
    return result, True, 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    operations = parser.add_subparsers(dest="operation", required=True)
    for name in ("inspect", "probe", "checkout"):
        operations.add_parser(name)
    qualify = operations.add_parser("qualify")
    qualify.add_argument("--candidate", required=True)
    promote = operations.add_parser("promote")
    promote.add_argument("--candidate", required=True)
    promote.add_argument("--request-id", required=True)
    status = operations.add_parser("request-status")
    status.add_argument("--request-id", required=True)
    args = parser.parse_args()
    state = json.loads(args.state.read_text(encoding="utf-8"))
    result, changed, code = operate(state, args.operation, getattr(args, "candidate", None), getattr(args, "request_id", None))
    if changed:
        args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
