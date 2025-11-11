import hashlib
from dataclasses import dataclass

from ..config import get_settings

REPO_REMOTE_URL = "git@github.com:GokalpKoreken/Alpaco_FullStack_Case_StudyV2.git"
DEFAULT_SEED = "deadbeefcafe"
_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class PriorityCoefficients:
    a: int
    b: int
    c: int
    seed: str


def _is_hex_prefix(seed: str) -> bool:
    prefix = seed[:6].lower()
    return len(prefix) == 6 and all(char in _HEX_DIGITS for char in prefix)


def _normalized_seed(seed: str) -> str:
    value = seed if _is_hex_prefix(seed) else hashlib.sha256(seed.encode()).hexdigest()
    # ensure we have at least 6 characters to avoid index errors
    if len(value) < 6:
        value = (value * 2).ljust(6, "0")
    return value.lower()


def _compute_coefficients(seed: str) -> PriorityCoefficients:
    normalized = _normalized_seed(seed)
    a = 7 + (int(normalized[0:2], 16) % 5)
    b = 13 + (int(normalized[2:4], 16) % 7)
    c = 3 + (int(normalized[4:6], 16) % 3)
    return PriorityCoefficients(a=a, b=b, c=c, seed=normalized)


def get_seed() -> str:
    settings = get_settings()
    return settings.dropspot_seed or DEFAULT_SEED


def derive_seed(remote_url: str, first_commit_epoch: str, start_time: str) -> str:
    raw = f"{remote_url}|{first_commit_epoch}|{start_time}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def compute_priority_score(
    *,
    base: int,
    signup_latency_ms: int,
    account_age_days: int,
    rapid_actions: int,
) -> float:
    seed = get_seed()
    coeffs = _compute_coefficients(seed)
    priority_score = base + (signup_latency_ms % coeffs.a) + (account_age_days % coeffs.b) - (rapid_actions % coeffs.c)
    return float(priority_score)


__all__ = [
    "PriorityCoefficients",
    "compute_priority_score",
    "derive_seed",
    "get_seed",
    "REPO_REMOTE_URL",
]
