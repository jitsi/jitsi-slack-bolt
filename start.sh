#!/usr/bin/env sh

if [ -z "$SLACK_EVENTS_API_MODE" ]; then
    export SLACK_EVENTS_API_MODE="socket"
fi

if [ -z "$PORT" ]; then
    export PORT=3000
fi

if [ -z "$METRICS_PORT" ]; then
    export METRICS_PORT=8080
fi

if [ "$SLACK_EVENTS_API_MODE" = "socket" ]; then
    if [ -z "$SLACK_BOT_TOKEN" ]; then
        echo "ERROR: SLACK_BOT_TOKEN must be set for socket mode"
        exit 1
    fi
    if [ -z "$SLACK_APP_TOKEN" ]; then
        echo "ERROR: SLACK_APP_TOKEN must be set for socket mode"
        exit 1
    fi

elif [ "$SLACK_EVENTS_API_MODE" = "oauth" ]; then
    if [ -z "$SLACK_SIGNING_SECRET" ]; then
        echo "ERROR: SLACK_SIGNING_SECRET must be set for oauth mode"
        exit 1
    fi
    if [ -z "$SLACK_CLIENT_ID" ]; then
        echo "ERROR: SLACK_CLIENT_ID must be set for oauth mode"
        exit 1
    fi
    if [ -z "$SLACK_CLIENT_SECRET" ]; then
        echo "ERROR: SLACK_CLIENT_SECRET must be set for oauth mode"
        exit 1
    fi

else
    echo "ERROR: SLACK_EVENTS_API_MODE must be either 'socket' or 'oauth'"
    exit 1
fi

export PROMETHEUS_MULTIPROC_DIR=/tmp

cd src/jitsi_slack_bolt

if [ -n "$DEBUG_LEVEL" ] && [ "$DEBUG_LEVEL" = "debug" ]; then
    gunicorn --config gunicorn-config.py --reload app:app
else
    gunicorn --config gunicorn-config.py app:app
fi
