"""Umbrel's authenticated app gateway is the identity boundary.

No host port may expose this service directly. Retain Harvey's guard and its
CSRF/media-type checks; translate only validated same-host browser origins.
The upstream token stays server-side, never in HTML, logs or the browser.
"""

from harvey import dashboard_auth as auth
from starlette.responses import PlainTextResponse


class UmbrelGateway:
    def __init__(self, app, store):
        self.app = app
        self.store = store

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = scope.get("headers", [])
        values = lambda name: [v.decode("latin-1") for k, v in headers if k.lower() == name]
        hosts, origins, sites = values(b"host"), values(b"origin"), values(b"sec-fetch-site")
        valid_host = len(hosts) == 1 and auth.parse_host(hosts[0]) is not None
        valid_origin = not origins or (valid_host and len(origins) == 1 and origins[0].lower() in
                                      (f"http://{hosts[0].lower()}", f"https://{hosts[0].lower()}"))
        if not valid_host or not valid_origin or len(sites) > 1:
            return await PlainTextResponse("Invalid dashboard origin", status_code=403,
                                           headers={"Cache-Control": "no-store"})(scope, receive, send)
        translated = [(k, v) for k, v in headers if k.lower() not in
                      (b"host", b"origin", b"authorization")]
        translated.append((b"host", b"127.0.0.1:5555"))
        if origins:
            translated.append((b"origin", b"http://127.0.0.1:5555"))
        translated.append((b"authorization", f"Bearer {self.store.get()}".encode("ascii")))
        return await self.app({**scope, "headers": translated}, receive, send)


if __name__ == "__main__":
    import uvicorn
    from harvey.dashboard import app, token_store

    token_store.get()  # Fail closed before listening if the private token cannot be loaded.
    uvicorn.run(UmbrelGateway(app, token_store), host="0.0.0.0", port=5555,
                proxy_headers=False, server_header=False, date_header=False)
