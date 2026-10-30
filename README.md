# Harvey for umbrelOS

Independent community package of [Harvey](https://github.com/ethanplusai/harvey), pinned to upstream commit `8023a9495eb46d644f03da8c8f4d2b9e41e5836e` (0.2.1). Currently built for x86-64 Umbrel devices.

## Install

In Umbrel's App Store, open Community App Stores and add:

```
https://github.com/Nath-vfx/umbrel-harvey
```

Open Harvey Community Store, install Harvey, then open its desktop icon. Umbrel manages installation, startup, stopping, updates and uninstallation. The standard app authentication remains enabled. No system packages or standalone host containers need to be installed manually.

## Setup

Installation starts the dashboard, not the prospecting/sending loop. Complete the dashboard checklist before explicitly starting Harvey. Configure the product, mailbox and approval/sending settings yourself; installation provides no subscription or mailbox credentials and sends no mail. A successful Start persists restart intention only after the native PID/lock is confirmed. Stop disables that intention before draining current work; Controls shows “Arrêt en cours” until it finishes. Container/application shutdown preserves intention, so use Stop when you do not want the heartbeat to resume.

Claude Code and Codex CLIs are included. For provider login, use Settings → Advanced → Terminal → Harvey → server in Umbrel. `harvey` invokes the bundled CLI from its persistent workspace. Use the provider's supported login procedure and then select that provider in Harvey. Subscription availability and usage terms remain the provider's responsibility.

## Data and security

All app state lives in Umbrel's app-managed `data` root mounted at `/app`: configuration, `.env`, SQLite database, prompts, skills and provider home (`/app/home`). Back up this root; it contains secrets. The real Python environment is included in the image; its `/app/.venv` link points to `/opt/venv`. Shipped Python application code is refreshed on container startup, while user configuration, prompts, skills and logins are retained. Umbrel uninstallation can remove app data: back it up first.

Before an update, pause sending, stop the heartbeat gracefully, then stop Harvey through Umbrel and take a private offline copy of the **whole** workspace, including hidden directories and SQLite/WAL. Keep the previous image reference. Restore into an isolated workspace with heartbeat intention disabled, sending paused and approval required before starting it. Check SQLite integrity and private login-directory permissions without printing secrets.

For scheduled encrypted backups, use Umbrel Settings → Backups → Configure → External drive. Never format or erase an existing drive as part of this package update. Escrow the recovery key in an authorized password manager (for example 1Password), then prove a native isolated restore includes the whole workspace. An offline archive test is not proof of native backup recovery. Do not start a commercial pilot until native restoration, actual provider access and a real maintenance-window reboot have been verified.

Harvey's upstream dashboard is loopback-only. This package exposes an internal Docker endpoint **only to Umbrel's authenticated app gateway**. The transport adapter validates the browser origin, retains the upstream request guard and JSON-body enforcement, and supplies the private upstream bearer token server-side. No token is embedded in the browser or public package. The browser's own API calls include the same-origin Umbrel session. Do not add a host `ports` mapping, disable app authentication, or expose this service using another unauthenticated proxy.

## Maintenance and check

### Maintenance-only Codex pin

`ghcr.io/nath-vfx/harvey-umbrel:8023a949-3-codex-0.159.3` derives directly from the installed `8023a949-3` runtime, pinned to base digest `sha256:9d3884424dff3479dbd86346c92e6ab1ae0c18d686839a07501e776d973e06b7`. Its only runtime change is installing npm `@openai/codex@0.159.3` as root, then restoring `USER harvey`. It retains the original Python runtime and does **not** contain the autonomy cutover described below.

The separate, manual `codex-pin.yml` workflow builds `codex-pin/Dockerfile`, checks the exact CLI version with the installed Python adapter, then exercises the actual dashboard in a fresh credential-free, network-disabled container. It requires stopped/no-PID and approval state both before and after restart, and only then publishes the immutable tag. It never starts a campaign or sends mail. This maintenance workflow does not rebuild the autonomy image, change the Umbrel manifest, or deploy to an installed app.

### Autonomy image

The image workflow uses the pinned upstream Dockerfile plus the runtime additions in `packaging`. It applies `browser-auth.patch`, then `autonomy.patch`; the latter includes the behavioral regressions. The build runs the full upstream suite and `packaging/test_gateway.py`, which checks same-origin access, cross-origin rejection, JSON enforcement and token privacy using the real upstream guard. A fresh isolated container must stay stopped and in approval across a Stop/restart before the image is published. This is not the credentialed Gmail/Calendly or host-reboot acceptance test. To run the gateway check separately with Harvey's dependencies installed:

```
PYTHONPATH=/path/to/harvey:packaging python packaging/test_gateway.py
```

To upgrade upstream, update its pinned commit in the workflow, the image tag and manifest version, then build/publish the image before applying the update through Umbrel. New upstream versions are not installed automatically.

Published release tags are immutable: the workflow refuses an existing tag. Choose a new tag for a later release rather than overwriting one already installed. The package uses `restart: unless-stopped` and a 31-minute Docker stop grace period; the heartbeat gets a single asynchronous drain of up to 30 minutes. Phase, last completed cycle and blockers are visible separately from the HTTP healthcheck. Validate the actual Umbrel reboot path, not just these declarations.

The bounded local-outreach profile is opt-in (`prospecting.enabled`). It uses only explicitly selected free discovery and ZeroBounce verification with durable budgets, sourced eligibility, separate first-contact limits, J+4/J+10 followups and a business window covering replies too. Calendly is read-only and fails closed for cold outreach when sync is incomplete. French refusals and legal/commercial exceptions remain held. Prepare private `harvey.local.yaml` and `skills/product_knowledge.md`; never put real business/contact data, provider keys or OAuth tokens in this public store.

## Package changes

- Maintenance-only `8023a949-3-codex-0.159.3`: pin the supported Codex CLI while retaining the installed `8023a949-3` runtime; no autonomy cutover or deployment.

- `0.2.1-umbrel.5`: opt-in bounded outreach and read-only calendar reconciliation; durable Start/Stop intention, visible loop health and graceful drain; full behavioral/security build checks and immutable image publication.

- `0.2.1-umbrel.4`: initialize private persistent provider login directories before startup.
- `0.2.1-umbrel.3`: include the upstream MIT copyright and permission notice in the distributed image.
- `0.2.1-umbrel.2`: use the real bundled Python virtual environment, so the first-run checklist reflects the installed runtime.
- `0.2.1-umbrel.1`: initial native package, persistent workspace, provider CLIs and authenticated dashboard adaptation.
