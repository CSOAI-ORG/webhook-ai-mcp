#!/usr/bin/env python3
"""Webhook AI MCP — MEOK AI Labs. Webhook validation, event logging, replay, and debugging."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, hashlib, hmac, time
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("webhook-ai", instructions="Webhook management and debugging. Validate signatures, log events, replay, and analyze webhook traffic. By MEOK AI Labs.")

_EVENT_LOG: list[dict] = []
_ENDPOINTS: dict[str, dict] = {}

SIGNATURE_SCHEMES = {
    "sha256": lambda payload, secret: hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest(),
    "sha1": lambda payload, secret: hmac.new(secret.encode(), payload.encode(), hashlib.sha1).hexdigest(),
    "md5": lambda payload, secret: hashlib.md5(f"{payload}{secret}".encode()).hexdigest(),
}


@mcp.tool()
def validate_webhook_signature(payload: str, signature: str, secret: str, scheme: str = "sha256", api_key: str = "") -> str:
    """Validate a webhook signature against a payload and secret. Supports sha256, sha1, md5."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    scheme = scheme.lower()
    if scheme not in SIGNATURE_SCHEMES:
        return {"error": f"Unknown scheme '{scheme}'. Supported: {', '.join(SIGNATURE_SCHEMES.keys())}"}

    expected = SIGNATURE_SCHEMES[scheme](payload, secret)
    # Strip common prefixes
    sig_clean = signature.replace(f"sha256=", "").replace(f"sha1=", "").strip()

    valid = hmac.compare_digest(sig_clean, expected)
    return {
        "valid": valid,
        "scheme": scheme,
        "expected_prefix": expected[:12] + "...",
        "received_prefix": sig_clean[:12] + "...",
        "payload_length": len(payload),
    }


@mcp.tool()
def log_webhook_event(event_type: str, source: str, payload: str = "{}", headers: str = "{}", status_code: int = 200, api_key: str = "") -> str:
    """Log a webhook event for debugging and replay."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    event_id = f"evt-{hashlib.sha256(f'{source}{time.time_ns()}'.encode()).hexdigest()[:16]}"
    entry = {
        "event_id": event_id,
        "event_type": event_type,
        "source": source,
        "payload": payload[:10000],
        "headers": headers[:2000],
        "status_code": status_code,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    _EVENT_LOG.append(entry)

    # Keep log manageable
    if len(_EVENT_LOG) > 1000:
        _EVENT_LOG[:] = _EVENT_LOG[-500:]

    return {"event_id": event_id, "status": "logged", "total_events": len(_EVENT_LOG)}


@mcp.tool()
def replay_events(source: str = "", event_type: str = "", limit: int = 20, api_key: str = "") -> str:
    """Replay/retrieve logged webhook events with optional filters."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    filtered = _EVENT_LOG
    if source:
        filtered = [e for e in filtered if e["source"] == source]
    if event_type:
        filtered = [e for e in filtered if e["event_type"] == event_type]

    recent = filtered[-limit:]
    recent.reverse()

    # Summary stats
    sources = defaultdict(int)
    types = defaultdict(int)
    for e in _EVENT_LOG:
        sources[e["source"]] += 1
        types[e["event_type"]] += 1

    return {
        "events": recent,
        "total_matching": len(filtered),
        "total_logged": len(_EVENT_LOG),
        "sources": dict(sources),
        "event_types": dict(types),
    }


@mcp.tool()
def register_endpoint(name: str, url: str, secret: str = "", events: str = "*", api_key: str = "") -> str:
    """Register a webhook endpoint for monitoring."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    endpoint_id = f"ep-{hashlib.sha256(f'{name}{url}'.encode()).hexdigest()[:12]}"
    _ENDPOINTS[endpoint_id] = {
        "name": name,
        "url": url,
        "secret_set": bool(secret),
        "events": events,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "delivery_count": 0,
        "failure_count": 0,
    }
    return {"endpoint_id": endpoint_id, "name": name, "status": "registered"}


@mcp.tool()
def generate_webhook_secret(length: int = 32, api_key: str = "") -> str:
    """Generate a cryptographically secure webhook signing secret."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    secret = hashlib.sha256(os.urandom(64)).hexdigest()[:length]
    return {
        "secret": f"whsec_{secret}",
        "length": length,
        "algorithm": "sha256",
        "usage": "Set as WEBHOOK_SECRET env var and use to validate incoming signatures",
    }


if __name__ == "__main__":
    mcp.run()
