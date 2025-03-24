#!/usr/bin/env python3
from app import when_ready, child_exit
from os import getenv

gunicorn_workers = getenv("GUNICORN_WORKERS", "1")
http_port = getenv("PORT", "3000")
debug_level = getenv("DEBUG_LEVEL", "info").lower()

bind = "0.0.0.0:" + http_port
workers = int(gunicorn_workers)
loglevel = debug_level

# Server Hooks
when_ready = when_ready
child_exit = child_exit
