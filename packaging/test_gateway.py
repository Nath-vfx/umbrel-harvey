"""Run with Harvey dependencies and package source on PYTHONPATH."""
import asyncio
import tempfile
from pathlib import Path

import httpx
from starlette.responses import JSONResponse

from harvey.dashboard_auth import DashboardGuard, TokenStore
from harvey_umbrel import UmbrelGateway


async def check():
    async def endpoint(scope, receive, send):
        await JSONResponse({"ok": True})(scope, receive, send)

    with tempfile.TemporaryDirectory() as directory:
        store = TokenStore(Path(directory) / "token")
        app = UmbrelGateway(DashboardGuard(endpoint, store), store)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app),
                                     base_url="http://umbrel.local:5555") as client:
            response = await client.post("/api/settings", json={}, headers={
                "Origin": "http://umbrel.local:5555", "Sec-Fetch-Site": "same-origin"})
            assert response.status_code == 200 and response.json() == {"ok": True}
            assert store.get() not in response.text
            assert response.headers["cache-control"] == "no-store"
            for headers in (
                {"Origin": "https://evil.example"},
                {"Origin": "null"},
                {"Sec-Fetch-Site": "cross-site"},
                {"Sec-Fetch-Site": "same-site"},
                [("Host", "umbrel.local:5555"), ("Host", "evil.example")],
                [("Origin", "http://umbrel.local:5555"), ("Origin", "https://evil.example")],
                {"Host": ""},
            ):
                response = await client.post("/api/settings", json={}, headers=headers)
                assert response.status_code == 403, (headers, response.status_code)
            response = await client.post("/api/settings", content="email=attacker",
                                         headers={"Content-Type": "application/x-www-form-urlencoded"})
            assert response.status_code == 415
            response = await client.get("/api/settings", headers={
                "Host": "harvey.umbrel.local", "Origin": "https://harvey.umbrel.local"})
            assert response.status_code == 200
            assert (Path(directory) / "token").stat().st_mode & 0o077 == 0
    print("Gateway security check passed: same-origin access, cross-origin rejection, JSON enforcement, private token.")


if __name__ == "__main__":
    asyncio.run(check())
