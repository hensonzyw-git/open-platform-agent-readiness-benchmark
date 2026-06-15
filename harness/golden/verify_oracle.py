"""
Verify our reference signer against POP's own worked example.
If we can reproduce A0BC221AB4EF5190EFD7D593566C6747, our golden oracle is trustworthy.
"""
import hashlib

EXPECTED = "A0BC221AB4EF5190EFD7D593566C6747"
APP_SECRET = "fb91e9e96f054166b567eec1b170ae2b"

# The exact sign-string the doc shows (stringA), before appending appSecret.
# Note: doc's input JSON had timestamp=1603354338917, but the sign string shows
# 1603353500369. We test the value the doc actually used in the sign string.
obj = (
    "%7B%22spu_id%22%3A81293%2C%22sku_id%22%3A487752589%2C%22bar_code%22%3A%22487752589%22"
    "%2C%22article_number%22%3A%22wucaishi%22%2C%22appoint_num%22%3A10%2C%22brand_id%22%3A10444"
    "%2C%22category_id%22%3A46%7D"
)
stringA = (
    "app_key=4d1715e032c44b709ef4954ef13e0950"
    "&appoint_no=A14343543654"
    f"&sku_list={obj}%2C{obj}"
    "&timestamp=1603353500369"
)
string_sign_temp = stringA + APP_SECRET
got = hashlib.md5(string_sign_temp.encode("utf-8")).hexdigest().upper()

print("reconstructed-from-doc-string :", got, "==", EXPECTED, "->", got == EXPECTED)
