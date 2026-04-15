# Webhook Ai

> By [MEOK AI Labs](https://meok.ai) — Webhook management and debugging. Validate signatures, log events, replay, and analyze webhook traffic. By MEOK AI Labs.

Webhook AI MCP — MEOK AI Labs. Webhook validation, event logging, replay, and debugging.

## Installation

```bash
pip install webhook-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install webhook-ai-mcp
```

## Tools

### `validate_webhook_signature`
Validate a webhook signature against a payload and secret. Supports sha256, sha1, md5.

**Parameters:**
- `payload` (str)
- `signature` (str)
- `secret` (str)
- `scheme` (str)

### `log_webhook_event`
Log a webhook event for debugging and replay.

**Parameters:**
- `event_type` (str)
- `source` (str)
- `payload` (str)
- `headers` (str)
- `status_code` (int)

### `replay_events`
Replay/retrieve logged webhook events with optional filters.

**Parameters:**
- `source` (str)
- `event_type` (str)
- `limit` (int)

### `register_endpoint`
Register a webhook endpoint for monitoring.

**Parameters:**
- `name` (str)
- `url` (str)
- `secret` (str)
- `events` (str)

### `generate_webhook_secret`
Generate a cryptographically secure webhook signing secret.

**Parameters:**
- `length` (int)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/webhook-ai-mcp](https://github.com/CSOAI-ORG/webhook-ai-mcp)
- **PyPI**: [pypi.org/project/webhook-ai-mcp](https://pypi.org/project/webhook-ai-mcp/)

## License

MIT — MEOK AI Labs
