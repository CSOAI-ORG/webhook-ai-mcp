#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, hashlib, time
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("webhook-ai-mcp")
_LOG: list = []
@mcp.tool(name="validate_webhook_signature")
async def validate_webhook_signature(payload: str, signature: str, secret: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    expected = hashlib.sha256(f"{payload}{secret}".encode()).hexdigest()
    return {"valid": signature == expected}
@mcp.tool(name="webhook_log")
async def webhook_log(event: str, source: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    entry = {"ts": time.time(), "event": event, "source": source}
    _LOG.append(entry)
    return {"logged": True, "entries": len(_LOG)}
@mcp.tool(name="replay_events")
async def replay_events(source: str, limit: int = 10, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    return {"events": [e for e in _LOG if e["source"] == source][:limit]}
    return {"events": [e for e in _LOG if e["source"] == source][:limit]}
if __name__ == "__main__":
    mcp.run()
