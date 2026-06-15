# POP (POIZON Open Platform) — Authentication & Signature (doc snapshot)

Source: https://open.poizon.com/doc/list/documentationDetail/9 (captured 2026-06-16)
This is the ONLY material the agent-under-test may use.

## Step 4: Generate Your Signature

### 1. Signature Generation Method

First, set all the data to be sent as a JSON object, add `appKey` and `timestamp`
(current timestamp in milliseconds) to this JSON object, then sort the parameters
with non-empty keys in the JSON object in ascending order based on ASCII value
(lexicographical order). Use URL key-value pair format (i.e., `a=a&b=b…`) to
concatenate into a string called `stringA`. Important rules:

- Parameter names are sorted in ascending order based on ASCII values (lexicographical order).
- If a parameter's value is empty, it does not participate in the signature.
- Parameter names and values are case-sensitive.
- Parameter values need to be URL-encoded (UTF-8 encoded).
- If a parameter value is a JSON array, concatenate the JSON objects in the array
  with commas to form the parameter value.
- When concatenating key and value, use Java's `URLEncoder.encode()`, reference:
  `URLEncoder.encode(String.valueOf(key), "UTF-8") + "=" + URLEncoder.encode(String.valueOf(value), "UTF-8") + "&"`

Then, append `appSecret` to the end of `stringA` to get the `stringSignTemp`
string. Perform MD5 (32-bit) calculation on `stringSignTemp`, and convert all
characters of the resulting string to uppercase to obtain the `sign` value.

### Signature Example

Request parameters before signing:

```json
{
  "app_key":"4d1715e032c44b709ef4954ef13e0950",
  "appoint_no":"A14343543654",
  "sku_list":[
    {"spu_id":81293,"sku_id":487752589,"bar_code":"487752589","article_number":"wucaishi","appoint_num":10,"brand_id":10444,"category_id":46},
    {"spu_id":81293,"sku_id":487752589,"bar_code":"487752589","article_number":"wucaishi","appoint_num":10,"brand_id":10444,"category_id":46}
  ],
  "timestamp":1603354338917
}
```

Signature Result: `A0BC221AB4EF5190EFD7D593566C6747`

### 2. Signature Reference (Python)

```python
def calculate_sign(self, key_dict: dict):
    sort_key_list = sorted(list(key_dict.keys()))
    new_str = ""
    prams = {}
    for key in sort_key_list:
        value = key_dict.get(key)
        prams[key] = getStr(value)
        valueStr = quote_plus(prams[key], 'utf-8')
        new_str = new_str + key + "=" + valueStr + "&"
    new_key = new_str[:-1] + self.app_secret
    m = hashlib.md5()
    m.update(new_key.encode('UTF-8'))
    sign = m.hexdigest().upper()
    return sign, new_str[:-1]
```

(Node.js reference additionally does `paramsStr = paramsStr.replace(/%20/gi, '+')`
so spaces are encoded as `+`.)
