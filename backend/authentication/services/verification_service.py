"""
Email verification:
- Cache
- TTL 10 min
- Hashed code
"""

import random
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
import secrets

VERIFICATION_TTL = 600


def generate_code():
    return str(secrets.randbelow(900000) + 100000)


def create_verification(user):
    raw_code = generate_code()
    hashed_code = make_password(raw_code)

    cache_key = f"verify_code:{user.id}"
    cache.set(cache_key, hashed_code, timeout=VERIFICATION_TTL)

    return raw_code


def verify_code(user, input_code):
    cache_key = f"verify_code:{user.id}"
    stored_hash = cache.get(cache_key)

    if not stored_hash:
        return False

    if not check_password(input_code, stored_hash):
        return False

    cache.delete(cache_key)
    return True