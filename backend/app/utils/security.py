"""Security utilities for password/key hashing."""

import bcrypt


def hash_key(key: str) -> str:
    """Hash a key using bcrypt."""
    return bcrypt.hashpw(key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_key(plain_key: str, hashed_key: str) -> bool:
    """Verify a plain key against a hashed key."""
    try:
        return bcrypt.checkpw(plain_key.encode('utf-8'), hashed_key.encode('utf-8'))
    except Exception:
        return False
