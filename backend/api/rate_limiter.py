"""
Rate Limiter Module

Purpose: Token bucket algorithm for API rate limiting.
Prevents exceeding API quotas and getting banned.

From PLAN.md:
- Pro Plan: 25 requests per minute for REST API
- Token bucket algorithm with burst allowance and gradual refill
"""

import time
import threading
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter.

    Features:
    - Maximum rate_limit requests per period seconds
    - Burst allowance (can make multiple requests quickly)
    - Automatic refill over time
    - Thread-safe
    """

    def __init__(self, rate_limit: int, period: int):
        """
        Initialize rate limiter.

        Args:
            rate_limit: Maximum number of requests allowed
            period: Time period in seconds
        """
        self.rate_limit = rate_limit  # requests
        self.period = period  # seconds
        self.tokens = rate_limit  # Start with full bucket
        self.last_update = time.time()
        self._lock = threading.Lock()

        logger.info(f"Initialized RateLimiter: {rate_limit} requests per {period} seconds")

    def wait_if_needed(self) -> None:
        """
        Wait if rate limit would be exceeded.
        Blocks until a token is available.

        This method implements the token bucket algorithm:
        1. Calculate time passed since last update
        2. Refill tokens based on elapsed time
        3. If no tokens available, wait for refill
        4. Consume one token
        """
        with self._lock:
            now = time.time()

            # Calculate elapsed time and refill tokens
            elapsed = now - self.last_update
            tokens_to_add = elapsed * (self.rate_limit / self.period)

            self.tokens = min(self.rate_limit, self.tokens + tokens_to_add)
            self.last_update = now

            # Wait if no tokens available
            if self.tokens < 1:
                # Calculate how long to wait for one token
                wait_time = (1.0 / self.rate_limit) * self.period
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)

                # Refill after waiting
                self.tokens = self.rate_limit
                self.last_update = time.time()

            # Consume one token
            self.tokens -= 1

            logger.debug(f"Token consumed. Remaining tokens: {self.tokens:.2f}")

    def get_available_tokens(self) -> float:
        """
        Get current available tokens without consuming.

        Returns:
            Number of available tokens
        """
        with self._lock:
            # Update tokens based on elapsed time
            now = time.time()
            elapsed = now - self.last_update
            tokens_to_add = elapsed * (self.rate_limit / self.period)

            available = min(self.rate_limit, self.tokens + tokens_to_add)
            return available

    def reset(self) -> None:
        """Reset rate limiter to full capacity."""
        with self._lock:
            self.tokens = self.rate_limit
            self.last_update = time.time()
            logger.warning("RateLimiter reset to full capacity")
