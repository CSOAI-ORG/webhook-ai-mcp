#!/usr/bin/env python3
import json, hashlib, time
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("webhook-ai-mcp")
_LOG: list = []
@mcp.tool(name="validate_webhook_signature")
async def validate_webhook_signature(payload: str, signature: str, secret: str) -> str:
    expected = hashlib.sha256(f"{payload}{secret}".encode()).hexdigest()
    return json.dumps({"valid": signature == expected})
@mcp.tool(name="webhook_log")
async def webhook_log(event: str, source: str) -> str:
    entry = {"ts": time.time(), "event": event, "source": source}
    _LOG.append(entry)
    return json.dumps({"logged": True, "entries": len(_LOG)})
@mcp.tool(name="replay_events")
async def replay_events(source: str, limit: int = 10) -> str:
    return json.dumps({"events": [e for e in _LOG if e["source"] == source][:limit]})
if __name__ == "__main__":
    mcp.run()
