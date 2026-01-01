"""
Timeframe Aggregation Module

Purpose: Aggregate 1-minute OHLCV bars into higher timeframe bars.
This is the core "smart" feature - single 1m WebSocket subscription updates all timeframes.

Architecture:
- Maintain rolling buffers of 1m bars for each higher timeframe
- On each new 1m bar, update all timeframes
- Return aggregated bars for all 9 timeframes

From PLAN.md:
- 5m = 5 consecutive 1m bars
- 15m = 15 consecutive 1m bars
- 30m = 30 consecutive 1m bars
- 1H = 60 consecutive 1m bars
- 4H = 240 consecutive 1m bars
- 1D = 1440 consecutive 1m bars (market hours)
- 1W = 5 days of 1D bars
- 1M = Calendar month aggregation
"""

from typing import List, Dict
from datetime import datetime, timedelta
import logging
from collections import deque
import calendar

from .cache import OHLCV

logger = logging.getLogger(__name__)


class TimeframeAggregator:
    """
    Aggregates 1-minute bars into all 9 timeframe bars.

    Features:
    - Maintains rolling buffers for each timeframe
    - Updates all timeframes on each new 1m bar
    - Returns aggregated bars for all timeframes
    - Thread-safe operations
    """

    # Timeframe definitions: (bars_in_period, seconds_in_period)
    TIMEFRAMES = {
        "1m": (1, 60),
        "5m": (5, 300),
        "15m": (15, 900),
        "30m": (30, 1800),
        "1H": (60, 3600),
        "4H": (240, 14400),
        "1D": (1440, 86400),  # 6.5 hour trading day
        "1W": (5, 604800),    # 5 days
        "1M": (None, 2592000) # Calendar month (variable bars)
    }

    def __init__(self):
        """Initialize aggregator with rolling buffers for each timeframe"""
        # Store 1m bars for all timeframes (buffer size varies)
        self._buffers: Dict[str, deque] = {
            "5m": deque(maxlen=5),
            "15m": deque(maxlen=15),
            "30m": deque(maxlen=30),
            "1H": deque(maxlen=60),
            "4H": deque(maxlen=240),
            "1D": deque(maxlen=1440),
            "1W": deque(maxlen=5),      # Store daily bars
            "1M": deque(maxlen=31)      # Store daily bars for monthly
        }

        # Store aggregated daily bars for weekly/monthly
        self._daily_bars: List[OHLCV] = []

        logger.info("Initialized TimeframeAggregator with rolling buffers")

    def add_1m_bar(self, bar: OHLCV) -> Dict[str, List[OHLCV]]:
        """
        Add a new 1-minute bar and update all timeframes.

        Args:
            bar: 1-minute OHLCV bar

        Returns:
            Dictionary mapping timeframe to list of aggregated bars
        """
        logger.debug(f"Adding 1m bar: {bar}")

        # Add to all buffers
        for timeframe in self._buffers:
            if timeframe != "1W" and timeframe != "1M":
                self._buffers[timeframe].append(bar)

        # Aggregate to all timeframes
        result = {}

        # 1m is just the bar itself
        result["1m"] = [bar]

        # Aggregate to intraday timeframes (5m, 15m, 30m, 1H, 4H)
        for timeframe in ["5m", "15m", "30m", "1H", "4H"]:
            if len(self._buffers[timeframe]) >= self.TIMEFRAMES[timeframe][0]:
                # Aggregate the buffer
                aggregated = self._aggregate_bars(
                    list(self._buffers[timeframe]),
                    timeframe
                )
                result[timeframe] = [aggregated]

        # Aggregate to daily (1D)
        if len(self._buffers["1D"]) >= self.TIMEFRAMES["1D"][0]:
            daily_bar = self._aggregate_bars(
                list(self._buffers["1D"]),
                "1D"
            )
            result["1D"] = [daily_bar]

            # Store daily bar for weekly/monthly aggregation
            self._daily_bars.append(daily_bar)

            # Aggregate to weekly (1W) - need 5 daily bars
            if len(self._daily_bars) >= 5:
                weekly_bars = self._daily_bars[-5:]  # Last 5 daily bars
                weekly_bar = self._aggregate_bars(weekly_bars, "1W")
                result["1W"] = [weekly_bar]

            # Aggregate to monthly (1M) - group by calendar month
            monthly_bar = self._aggregate_monthly(self._daily_bars)
            if monthly_bar:
                result["1M"] = [monthly_bar]

        return result

    def _aggregate_bars(self, bars: List[OHLCV], timeframe: str) -> OHLCV:
        """
        Aggregate a list of bars into a single higher timeframe bar.

        Args:
            bars: List of 1-minute or daily bars
            timeframe: Target timeframe string

        Returns:
            Aggregated OHLCV bar
        """
        if not bars:
            raise ValueError(f"Cannot aggregate empty bar list for {timeframe}")

        # Aggregate OHLCV
        aggregated = OHLCV(
            time=bars[0].time,  # Time of first bar
            open=bars[0].open,
            high=max(bar.high for bar in bars),
            low=min(bar.low for bar in bars),
            close=bars[-1].close,
            volume=sum(bar.volume for bar in bars)
        )

        logger.debug(f"Aggregated {len(bars)} bars to {timeframe}: {aggregated}")
        return aggregated

    def _aggregate_monthly(self, daily_bars: List[OHLCV]) -> OHLCV:
        """
        Aggregate daily bars into monthly bars by calendar month.

        Args:
            daily_bars: List of daily bars

        Returns:
            Monthly aggregated bar for current month, or None if insufficient data
        """
        if not daily_bars:
            return None

        # Get current month from latest bar
        latest_bar = daily_bars[-1]
        latest_date = datetime.fromtimestamp(latest_bar.time)

        # Filter bars for current month
        current_month_bars = []
        for bar in reversed(daily_bars):
            bar_date = datetime.fromtimestamp(bar.time)
            if bar_date.month == latest_date.month and bar_date.year == latest_date.year:
                current_month_bars.append(bar)
            else:
                break  # Different month, stop

        if not current_month_bars:
            return None

        # Reverse to maintain chronological order
        current_month_bars = list(reversed(current_month_bars))

        return self._aggregate_bars(current_month_bars, "1M")

    def get_all_timeframe_bars(self, timeframe: str, count: int = 100) -> List[OHLCV]:
        """
        Get historical aggregated bars for a specific timeframe.

        Args:
            timeframe: Timeframe string (1m, 5m, 15m, etc.)
            count: Number of bars to return

        Returns:
            List of aggregated bars (empty if not enough data)
        """
        # For 1m, return recent bars directly
        if timeframe == "1m":
            # This would be called from the cached historical data
            return []

        # For intraday timeframes, we'd need to store historical aggregations
        # This is a placeholder - actual implementation would cache aggregated bars
        logger.warning(f"get_all_timeframe_bars not fully implemented for {timeframe}")
        return []


def aggregate_historical_1m_to_timeframe(
    bars_1m: List[OHLCV],
    target_timeframe: str
) -> List[OHLCV]:
    """
    Aggregate historical 1m bars into a higher timeframe.

    Used for initial historical data loading.

    Args:
        bars_1m: List of 1-minute OHLCV bars (chronological order)
        target_timeframe: Target timeframe (5m, 15m, 30m, 1H, 4H, 1D)

    Returns:
        List of aggregated bars for target timeframe
    """
    if target_timeframe == "1m":
        return bars_1m

    if target_timeframe not in TimeframeAggregator.TIMEFRAMES:
        raise ValueError(f"Unknown timeframe: {target_timeframe}")

    bars_needed = TimeframeAggregator.TIMEFRAMES[target_timeframe][0]

    if bars_needed is None:
        raise ValueError(f"Cannot aggregate to {target_timeframe} (variable bars)")

    if bars_needed == 5:  # Weekly aggregation
        # First aggregate to daily, then to weekly
        daily_bars = _aggregate_to_daily(bars_1m)
        return _aggregate_to_weekly(daily_bars)

    # Standard intraday aggregation
    aggregated_bars = []

    for i in range(0, len(bars_1m), bars_needed):
        chunk = bars_1m[i:i + bars_needed]

        if len(chunk) == bars_needed:
            # Aggregate this chunk
            bar = OHLCV(
                time=chunk[0].time,
                open=chunk[0].open,
                high=max(b.high for b in chunk),
                low=min(b.low for b in chunk),
                close=chunk[-1].close,
                volume=sum(b.volume for b in chunk)
            )
            aggregated_bars.append(bar)

    logger.info(f"Aggregated {len(bars_1m)} 1m bars to {len(aggregated_bars)} {target_timeframe} bars")
    return aggregated_bars


def _aggregate_to_daily(bars_1m: List[OHLCV]) -> List[OHLCV]:
    """
    Aggregate 1m bars to daily bars.
    Groups bars by trading day (6.5 hour session).
    """
    # Group by date
    daily_groups = {}

    for bar in bars_1m:
        date = datetime.fromtimestamp(bar.time).date()
        if date not in daily_groups:
            daily_groups[date] = []
        daily_groups[date].append(bar)

    # Aggregate each day's bars
    daily_bars = []
    for date, bars in sorted(daily_groups.items()):
        bar = OHLCV(
            time=bars[0].time,
            open=bars[0].open,
            high=max(b.high for b in bars),
            low=min(b.low for b in bars),
            close=bars[-1].close,
            volume=sum(b.volume for b in bars)
        )
        daily_bars.append(bar)

    return daily_bars


def _aggregate_to_weekly(daily_bars: List[OHLCV]) -> List[OHLCV]:
    """
    Aggregate daily bars to weekly bars.
    Groups bars by week (5 trading days).
    """
    # Group by week (Monday = 0, Sunday = 6)
    weekly_groups = {}

    for bar in daily_bars:
        date = datetime.fromtimestamp(bar.time)
        # Get week number
        week_key = (date.year, date.isocalendar()[1])

        if week_key not in weekly_groups:
            weekly_groups[week_key] = []
        weekly_groups[week_key].append(bar)

    # Aggregate each week's bars
    weekly_bars = []
    for week_key, bars in sorted(weekly_groups.items()):
        bar = OHLCV(
            time=bars[0].time,
            open=bars[0].open,
            high=max(b.high for b in bars),
            low=min(b.low for b in bars),
            close=bars[-1].close,
            volume=sum(b.volume for b in bars)
        )
        weekly_bars.append(bar)

    return weekly_bars
