import time

from app.services.rate_limiter import RateLimiter


def test_allows_up_to_the_limit_then_blocks():
    rl = RateLimiter(max_events=3, window_seconds=60)
    assert [rl.allow("client-a") for _ in range(3)] == [True, True, True]
    assert rl.allow("client-a") is False


def test_keys_are_independent():
    rl = RateLimiter(max_events=1, window_seconds=60)
    assert rl.allow("client-a") is True
    assert rl.allow("client-b") is True
    assert rl.allow("client-a") is False


def test_window_slides_and_frees_budget():
    rl = RateLimiter(max_events=2, window_seconds=0.2)
    assert rl.allow("c") is True
    assert rl.allow("c") is True
    assert rl.allow("c") is False
    time.sleep(0.25)
    assert rl.allow("c") is True


def test_retry_after_is_positive_when_blocked():
    rl = RateLimiter(max_events=1, window_seconds=60)
    rl.allow("c")
    assert rl.retry_after("c") > 0
    assert rl.retry_after("never-seen") == 0
