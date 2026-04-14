#!/usr/bin/env python3
"""Create and manage webhook endpoints. — MEOK AI Labs."""
import json, os, re, hashlib, uuid as _uuid, random
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": "Limit/day"})
    _usage[c].append(now); return None

mcp = FastMCP("webhook", instructions="MEOK AI Labs — Create and manage webhook endpoints.")


@mcp.tool()
def send_webhook(url: str, payload: str, method: str = "POST") -> str:
    """Send a webhook request."""
    if err := _rl(): return err
    import urllib.request
    try:
        data = payload.encode()
        req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=10)
        return json.dumps({"status": resp.status, "success": True}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)

@mcp.tool()
def create_webhook_config(name: str, url: str, events: str = "all") -> str:
    """Create a webhook configuration."""
    if err := _rl(): return err
    config = {"name": name, "url": url, "events": events.split(","), "created": datetime.now(timezone.utc).isoformat(), "id": hashlib.sha256(f"{name}{url}".encode()).hexdigest()[:8]}
    return json.dumps(config, indent=2)

if __name__ == "__main__":
    mcp.run()
