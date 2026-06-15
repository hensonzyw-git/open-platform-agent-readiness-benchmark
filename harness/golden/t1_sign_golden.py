"""
T1-sign golden: POP request signing.
Reference signer verified against POP's own worked example (see verify_oracle.py).
We deliberately pick a flat test vector that still exercises the real traps:
  - empty-value param must be DROPPED
  - space must encode as '+' (Java URLEncoder), not %20
  - string array joined by comma, then URL-encoded
  - appSecret appended directly (no '&'), MD5, UPPERCASE
"""
import hashlib
from urllib.parse import quote_plus


def pop_sign(params: dict, secret: str) -> str:
    items = []
    for k in sorted(params.keys()):  # ASCII ascending
        v = params[k]
        if v is None or v == "":      # empty values do not participate
            continue
        if isinstance(v, (list, tuple)):
            v = ",".join(str(x) for x in v)   # array -> comma-join
        items.append(f"{quote_plus(str(k))}={quote_plus(str(v))}")  # space -> '+'
    string_a = "&".join(items)
    string_sign_temp = string_a + secret   # appSecret appended directly, no '&'
    return string_a, hashlib.md5(string_sign_temp.encode("utf-8")).hexdigest().upper()


# ---- The fixed task input the agent-under-test must sign ----
TASK_PARAMS = {
    "app_key": "test_app_key_001",
    "timestamp": 1700000000000,
    "title": "Nike Air Max",     # space -> '+'
    "price": 15400,
    "skuId": 487752589,
    "remark": "",                # empty -> dropped
    "tags": ["new", "hot"],      # array -> "new,hot" -> url-encoded
}
TASK_SECRET = "test_secret_xyz"

if __name__ == "__main__":
    string_a, sign = pop_sign(TASK_PARAMS, TASK_SECRET)
    print("stringA:", string_a)
    print("GOLDEN sign:", sign)
