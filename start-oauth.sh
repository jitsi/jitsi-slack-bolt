#!/usr/bin/env sh

# expects SLACK_SIGNING_SECRET, SLACK_CLIENT_ID, and SLACK_CLIENT_SECRET to be set

python3 ./src/jitsi_slack_bolt/app.py
