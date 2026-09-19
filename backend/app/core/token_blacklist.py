"""
Token blacklist for logout / token revocation.

In development / single-process mode this in-memory set works correctly.
In production (multi-process / multi-replica), replace this with a
Redis SET with TTL matching the JWT expiry, e.g.:

    redis_client.setex(f"blacklist:{jti}", ACCESS_TOKEN_EXPIRE_SECONDS, "1")
    redis_client.exists(f"blacklist:{jti}") -> bool
"""
from typing import Set

# Stores raw token strings that have been explicitly revoked.
# Entries are never cleaned up in this simple implementation; a production
# deployment MUST replace this with a Redis SET with TTL.
_blacklisted_tokens: Set[str] = set()


def blacklist_token(token: str) -> None:
    """Add a token to the revocation list."""
    _blacklisted_tokens.add(token)


def is_token_blacklisted(token: str) -> bool:
    """Return True if the token has been explicitly revoked."""
    return token in _blacklisted_tokens
