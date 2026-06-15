"""
Scorer for T3 / Create Consignment Application (doc-only).
No single golden hash — instead criterion-based, with a sign-CONSISTENCY check:
we recompute the sign from the agent's OWN emitted params and require it to match
the sign the agent emitted. This tests "did the agent build a correctly-signed,
complete write request" the way real first-pass success is defined.

Usage: python3 score_t3.py <agent_output.json>
where agent_output.json = {"endpoint": "...", "params": { ... including "sign" ... }}
"""
import hashlib
import json
import sys
from urllib.parse import quote_plus

ENDPOINT = "https://open.poizon.com/dop/api/v1/pop/api/v1/deposit/enterprise-stock-apply/add"
REQUIRED_GENERAL = ["app_key", "access_token", "timestamp", "sign", "language", "timeZone"]
APP_SECRET = "test_secret_xyz"


def pop_sign(params: dict, secret: str) -> str:
    items = []
    for k in sorted(params.keys()):
        v = params[k]
        if v is None or v == "":
            continue
        if isinstance(v, (list, tuple)):
            v = ",".join(str(x) for x in v)
        items.append(f"{quote_plus(str(k))}={quote_plus(str(v))}")
    return hashlib.md5(("&".join(items) + secret).encode("utf-8")).hexdigest().upper()


def score(doc: dict) -> dict:
    params = doc.get("params", {})
    crit = {}
    # C1 correct endpoint
    crit["C1_endpoint"] = doc.get("endpoint", "").rstrip("/") == ENDPOINT
    # C2 all 6 required general params present and non-empty
    crit["C2_required_general"] = all(params.get(k) not in (None, "") for k in REQUIRED_GENERAL)
    # C3 uses skuId (not relying on globalSkuId)
    crit["C3_uses_skuId"] = params.get("skuId") not in (None, "")
    # C4 applyQty present
    crit["C4_applyQty"] = params.get("applyQty") not in (None, "")
    # C5 sign consistency: recompute over all params except 'sign'
    emitted = params.get("sign")
    signable = {k: v for k, v in params.items() if k != "sign"}
    recomputed = pop_sign(signable, APP_SECRET)
    crit["C5_sign_consistent"] = isinstance(emitted, str) and emitted.upper() == recomputed
    strict = all(crit.values())
    return {"criteria": crit, "criterion_pass_rate": sum(crit.values()) / len(crit),
            "strict_pass": strict, "recomputed_sign": recomputed, "emitted_sign": emitted}


if __name__ == "__main__":
    doc = json.load(open(sys.argv[1]))
    r = score(doc)
    for k, v in r["criteria"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"criterion_pass_rate={r['criterion_pass_rate']:.2f}  STRICT={'PASS' if r['strict_pass'] else 'FAIL'}")
    if not r["criteria"]["C5_sign_consistent"]:
        print(f"  emitted={r['emitted_sign']}  recomputed={r['recomputed_sign']}")
