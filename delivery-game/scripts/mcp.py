#!/usr/bin/env python3
"""Call the project's local Cocos MCP when it is open in Creator."""
import json
import os
import pathlib
import sys
import urllib.request

tool = sys.argv[1]
argument = sys.argv[2] if len(sys.argv) > 2 else '{}'
params = json.loads(pathlib.Path(argument[1:]).read_text() if argument.startswith('@') else argument)
body = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': tool, 'arguments': params}}
request = urllib.request.Request(os.environ.get('COCOS_MCP_URL', 'http://127.0.0.1:28917/'),
    data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'})
with urllib.request.urlopen(request, timeout=120) as response:
    message = json.load(response)
if 'error' in message:
    print(json.dumps(message['error'], ensure_ascii=False, indent=2))
    sys.exit(1)
result = message['result']
data = result.get('structuredContent') or result
print(json.dumps(data, ensure_ascii=False, indent=2))
if result.get('isError') or data.get('ok') is False:
    sys.exit(1)
