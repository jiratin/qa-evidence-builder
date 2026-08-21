import copy
import re

DEFAULT_SENSITIVE_KEYS = {
    "authorization", "x-authorization", "cookie", "set-cookie",
    "password", "passwd", "pin", "token", "access_token", "refresh_token",
    "session", "mfaf-session", "mobile", "mobileno", "phone", "email",
    "device", "deviceid", "mfaf-device"
}

JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
BEARER_RE = re.compile(r"(?i)(Bearer\s+)[A-Za-z0-9._~+/\-=]+")
EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-])[^@\s]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")

def _normalize_key(key):
    return str(key).lower().replace("-", "").replace("_", "")

def sensitive_keys(extra_keys=None):
    keys = set(DEFAULT_SENSITIVE_KEYS)
    for item in extra_keys or []:
        item = str(item).strip()
        if item:
            keys.add(item)
    return keys

def _sensitive(key, keys):
    normalized = _normalize_key(key)
    return any(_normalize_key(x) in normalized for x in keys)

def sanitize(value, extra_keys=None):
    keys = sensitive_keys(extra_keys)

    def walk(item):
        if isinstance(item, dict):
            return {
                k: ("********" if _sensitive(k, keys) else walk(v))
                for k, v in item.items()
            }

        if isinstance(item, list):
            return [walk(v) for v in item]

        if isinstance(item, str):
            item = BEARER_RE.sub(r"\1********", item)
            item = JWT_RE.sub("********", item)
            return EMAIL_RE.sub(r"\1***@\2", item)

        return copy.deepcopy(item)

    return walk(value)
