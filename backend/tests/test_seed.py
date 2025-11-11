from app.services import seed


def test_derive_seed_deterministic():
	remote = "git@github.com:alpaco/dropspot.git"
	epoch = "1700000000"
	start = "202511101942"
	value = seed.derive_seed(remote, epoch, start)
	assert value == seed.derive_seed(remote, epoch, start)
	assert len(value) == 12


def test_compute_priority_score_uses_seed(monkeypatch):
	monkeypatch.setattr(seed, "get_seed", lambda: "0123abcdffff")
	score = seed.compute_priority_score(
		base=10,
		signup_latency_ms=2500,
		account_age_days=12,
		rapid_actions=1,
	)
	assert isinstance(score, float)
	# manual expectation based on coefficients (a=7+1=8,b=13+2=15,c=3+(0)=3)
	expected = 10 + (2500 % 8) + (12 % 15) - (1 % 3)
	assert score == expected
