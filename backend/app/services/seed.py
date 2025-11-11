import hashlib
from dataclasses import dataclass

from ..config import get_settings

DEFAULT_SEED = "deadbeefcafe"


@dataclass(frozen=True)
class PriorityCoefficients:
    a: int
    b: int
    c: int
    seed: str


def _compute_coefficients(seed: str) -> PriorityCoefficients:
    a = 7 + (int(seed[0:2], 16) % 5)
    b = 13 + (int(seed[2:4], 16) % 7)
    c = 3 + (int(seed[4:6], 16) % 3)
    return PriorityCoefficients(a=a, b=b, c=c, seed=seed)


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
]
