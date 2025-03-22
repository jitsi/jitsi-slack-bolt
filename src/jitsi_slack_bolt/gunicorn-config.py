#!/usr/bin/env python3
from app import when_ready, child_exit
from os import getenv

http_port = getenv('PORT', '3000')
debug_level = getenv('DEBUG_LEVEL', 'info').lower() 

bind = '0.0.0.0:' + http_port
workers = 4
loglevel = debug_level

# Server Hooks
when_ready = when_ready
child_exit = child_exit