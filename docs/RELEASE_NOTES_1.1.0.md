# Orhun 1.1.0 Release Notes

Modern HTTP client for real-world API integrations.

## Highlights

### HTTP client in the core

```orhun
yanit olsun http.get("http://api.ornek/kullanicilar", {"Accept": "application/json"})
yaz yanit.durum
yaz yanit.govde
yaz yanit.basliklar["Content-Type"]

govde olsun json.yaz({"ad": "Orhun"})
yanit2 olsun http.post("http://api.ornek/kayit", govde, {"Content-Type": "application/json"})
```

| Method | Call |
| --- | --- |
| GET | `http.get(url, basliklar?)` |
| POST | `http.post(url, govde, basliklar?)` |
| PUT | `http.put(url, govde, basliklar?)` |
| DELETE | `http.delete(url, basliklar?)` |

Response object:

```orhun
{ "durum": 200, "govde": "...", "basliklar": { ... } }
```

- Custom request headers (JSON, Authorization, …)
- Response status **and** body/headers returned even for 4xx/5xx
- Same semantics in interpreter and VM (WinHTTP on Windows, sockets on Linux/macOS)
- Alias module name: `ag` (same functions as `http`)

### StdLib `orhun/http.oh`

Helpers: `get`/`post`/`put`/`sil`, `yanit_json`, `yanit_basari_mi`, `json_get`,
`json_post`, `bearer_get`.

### Example & gates

- `examples/http_api_ornek.oh`
- `tests/http_smoke.py` (local HTTP server, full method/header coverage)

## Compatibility

Additive. `internet.getir` / `internet.indir` remain available (GET body only).
HTTPS is still platform-limited on POSIX without extra deps; Windows WinHTTP
supports HTTPS.

## Verification

- Full case suite green
- `tests/http_smoke.py` green (8 scenarios)
- VM parity 153/0
- Release readiness green
