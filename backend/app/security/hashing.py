"""
Password hashing. bcrypt, via the `bcrypt` library directly (no passlib
dependency needed for a single algorithm). Never log a password or hash —
see PHASE_W12_REPORT.md, security hardening section.
"""
import bcrypt

_BCRYPT_ROUNDS = 12


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        # Malformed hash (e.g. corrupted data) — treat as non-matching,
        # never raise into the auth flow.
        return False
