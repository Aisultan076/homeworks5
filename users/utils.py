import random
from django.core.cache import cache

def generate_confirmation_code(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def save_code_to_cache(user_id, code, ttl=300):
    key = f"confirmation_code:{user_id}"
    cache.set(key, code, timeout=ttl)


def verify_code(user_id, code):
    key = f"confirmation_code:{user_id}"
    stored_code = cache.get(key)

    if stored_code and stored_code == code:
        cache.delete(key)
        return True
    return False