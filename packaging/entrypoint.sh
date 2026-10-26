#!/bin/sh
set -eu
umask 077
cd /app
mkdir -p data home
# Refresh only shipped code; user configuration, prompts, skills and logins survive.
ln -sfn /opt/venv /app/.venv
rm -rf /app/harvey
cp -a /opt/harvey/harvey /app/harvey
for name in harvey.yaml prompts skills; do
    if [ ! -e "/app/$name" ]; then
        cp -a "/opt/harvey/$name" "/app/$name"
    fi
done
if [ ! -e /app/.env ]; then
    cp /opt/harvey/.env.example /app/.env
fi
chmod 600 /app/.env
exec "$@"
