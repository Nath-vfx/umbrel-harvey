FROM ghcr.io/nath-vfx/harvey-umbrel:8023a949-3@sha256:9d3884424dff3479dbd86346c92e6ab1ae0c18d686839a07501e776d973e06b7

USER root
RUN npm install -g @openai/codex@0.159.3 \
    && test "$(codex --version)" = "codex-cli 0.159.3"
USER harvey
