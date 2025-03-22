#!/usr/bin/env python3
from app import when_ready, child_exit

bind = '0.0.0.0:3000'
workers = 2
loglevel = "info"

# Server Hooks
when_ready = when_ready
child_exit = child_exit