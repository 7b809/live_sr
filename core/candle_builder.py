from datetime import datetime

class CandleBuilder:
    def __init__(self, timeframe):
        self.timeframe = timeframe
        self.current = None

    def _round_time(self, ts):
        return ts.replace(second=0, microsecond=0,
            minute=(ts.minute // self.timeframe) * self.timeframe)

    def update(self, price, volume, ts):
        ct = self._round_time(ts)

        if self.current is None:
            self.current = self._new(ct, price, volume)
            return None

        if ct == self.current["time"]:
            self.current["high"] = max(self.current["high"], price)
            self.current["low"] = min(self.current["low"], price)
            self.current["close"] = price
            self.current["volume"] += volume
            return None

        finished = self.current
        self.current = self._new(ct, price, volume)
        return finished

    def _new(self, t, p, v):
        return {
            "time": t,
            "open": p,
            "high": p,
            "low": p,
            "close": p,
            "volume": v
        }