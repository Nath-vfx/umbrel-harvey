# Harvey for umbrelOS

Independent community package of [Harvey](https://github.com/ethanplusai/harvey), pinned to upstream commit `8023a9495eb46d644f03da8c8f4d2b9e41e5836e` (0.2.1). Currently built for x86-64 Umbrel devices.

## Install

In Umbrel's App Store, open Community App Stores and add:

```
https://github.com/Nath-vfx/umbrel-harvey
```

Open Harvey Community Store, install Harvey, then open its desktop icon. Umbrel manages installation, startup, stopping, updates and uninstallation. The standard app authentication remains enabled. No system packages or standalone host containers need to be installed manually.

## Setup

Installation starts the dashboard, not the prospecting/sending loop. Complete the dashboard checklist before explicitly starting Harvey. Configure the product, mailbox and approval/sending settings yourself; installation provides no subscription or mailbox credentials and sends no mail.

Claude Code and Codex CLIs are included. For provider login, use Settings → Advanced → Terminal → Harvey → server in Umbrel. `harvey` invokes the bundled CLI from its persistent workspace. Use the provider's supported login procedure and then select that provider in Harvey. Subscription availability and usage terms remain the provider's responsibility.

## Data and security

All app state lives in Umbrel's app-managed `data` root mounted at `/app`: configuration, `.env`, SQLite database, prompts, skills and provider home (`/app/home`). Back up this root; it contains secrets. The real Python environment is included in the image; its `/app/.venv` link points to `/opt/venv`. Shipped Python application code is refreshed on container startup, while user configuration, prompts, skills and logins are retained. Umbrel uninstallation can remove app data: back it up first.

Harvey's upstream dashboard is loopback-only. This package exposes an internal Docker endpoint **only to Umbrel's authenticated app gateway**. The transport adapter validates the browser origin, retains the upstream request guard and JSON-body enforcement, and supplies the private upstream bearer token server-side. No token is embedded in the browser or public package. The browser's own API calls include the same-origin Umbrel session. Do not add a host `ports` mapping, disable app authentication, or expose this service using another unauthenticated proxy.

## Maintenance and check

The image workflow uses the pinned upstream Dockerfile plus the small runtime additions in `packaging`. `packaging/test_gateway.py` runs during the image build and checks same-origin access, cross-origin rejection, JSON enforcement and token privacy using the real upstream guard. To run it separately with Harvey's dependencies installed:

```
PYTHONPATH=/path/to/harvey:packaging python packaging/test_gateway.py
```

To upgrade upstream, update its pinned commit in the workflow, the image tag and manifest version, then build/publish the image before applying the update through Umbrel. New upstream versions are not installed automatically.

## Package changes

- `0.2.1-umbrel.3`: include the upstream MIT copyright and permission notice in the distributed image.
- `0.2.1-umbrel.2`: use the real bundled Python virtual environment, so the first-run checklist reflects the installed runtime.
- `0.2.1-umbrel.1`: initial native package, persistent workspace, provider CLIs and authenticated dashboard adaptation.
