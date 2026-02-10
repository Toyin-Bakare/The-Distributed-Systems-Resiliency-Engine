from __future__ import annotations
from typing import Optional

def key_for_api_key(api_key: str, prefix: str) -> str:
    return f"{prefix}:apikey:{api_key}"

def key_for_user(user_id: str, prefix: str) -> str:
    return f"{prefix}:user:{user_id}"

def key_for_ip(ip: str, prefix: str) -> str:
    safe = ip.replace(':', '_')
    return f"{prefix}:ip:{safe}"

def pick_identity_key(prefix: str, api_key: Optional[str], user_id: Optional[str], ip: str) -> str:
    if api_key:
        return key_for_api_key(api_key, prefix)
    if user_id:
        return key_for_user(user_id, prefix)
    return key_for_ip(ip, prefix)
