# POP — Create Consignment Application (doc snapshot)

Source: https://open.poizon.com/doc/list/apiDetail/28 (captured 2026-06-16)
This + the signing rules below are the ONLY material the agent-under-test may use.

## Endpoint
`POST https://open.poizon.com/dop/api/v1/pop/api/v1/deposit/enterprise-stock-apply/add`

This API allows sellers to initiate a consignment request, sending products to a
designated warehouse for sale on consignment.

## General Parameters (all required)
| name | type | note | example |
|------|------|------|---------|
| app_key | String | Application identifier | app_key=your_app_key |
| access_token | String | Request token | access_token=your_access_token |
| timestamp | Long | Current timestamp (milliseconds) | timestamp=1648888888814 |
| sign | String | Signature (see signing rules) | sign=the_sign_string |
| language | String | Language: zh, zh-TW, en, ja, ko, fr | language=zh |
| timeZone | String | Time zone | timeZone=Asia/Shanghai |

## Business Parameters
| name | type | required | note | example |
|------|------|----------|------|---------|
| skuId | number | — | skuId and globalSkuId cannot both be empty. Input at least one. **Recommend to use skuId** | skuId=111 |
| globalSkuId | number | — | Product skuId. skuId and globalSkuId cannot both be empty. Input at least one. Recommend to use skuId | globalSkuId=111 |
| applyQty | number | required | Apply quantity | applyQty=1 |

## Request Sample (Payload)
```json
{ "skuId": 120007853, "applyQty": 1 }
```

## Response Sample (200)
```json
{ "root": { "code": 200, "data": "SA0001" } }
```

---

## Signing rules (from Authentication doc)
Set all the data to be sent as a JSON object, add app_key and timestamp (ms), then
sort non-empty params ascending by ASCII. Concatenate as `a=a&b=b` into stringA.
- empty-value params do not participate
- values URL-encoded (UTF-8), Java `URLEncoder.encode` semantics (space -> `+`)
- array values: join elements with commas, then encode
Append appSecret to end of stringA -> stringSignTemp. MD5 (32-bit), UPPERCASE -> sign.
(The `sign` field itself is NOT part of the signed string.)
