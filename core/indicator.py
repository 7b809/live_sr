from collections import deque

class SRIndicator:
    def __init__(self, lookback, vol_len, atr_period, box_mult):
        self.lb = lookback
        self.vol_len = vol_len
        self.atr_period = atr_period
        self.box_mult = box_mult

        self.vol_history = deque(maxlen=50)
        self.tr_history = deque(maxlen=atr_period)

        self.support = None
        self.support_zone = None

        self.resistance = None
        self.resistance_zone = None

        self.res_is_sup = False
        self.sup_is_res = False

    # ---------------- ATR ----------------
    def update_atr(self, prev, curr):
        tr = max(
            curr["high"] - curr["low"],
            abs(curr["high"] - prev["close"]),
            abs(curr["low"] - prev["close"])
        )
        self.tr_history.append(tr)

        if len(self.tr_history) < self.atr_period:
            return None

        return sum(self.tr_history) / len(self.tr_history)

    # ---------------- Volume Delta ----------------
    def volume_delta(self, c):
        return c["volume"] if c["close"] > c["open"] else -c["volume"]

    # ---------------- Pivot ----------------
    def pivot_high(self, data, i):
        if i < self.lb or i >= len(data) - self.lb:
            return None
        val = data[i]["high"]
        for j in range(1, self.lb+1):
            if data[i-j]["high"] >= val or data[i+j]["high"] >= val:
                return None
        return val

    def pivot_low(self, data, i):
        if i < self.lb or i >= len(data) - self.lb:
            return None
        val = data[i]["low"]
        for j in range(1, self.lb+1):
            if data[i-j]["low"] <= val or data[i+j]["low"] <= val:
                return None
        return val

    # ---------------- MAIN ----------------
    def run(self, data):
        signals = []

        for i in range(1, len(data)):
            curr = data[i]
            prev = data[i-1]

            vol = self.volume_delta(curr)
            self.vol_history.append(vol)

            if len(self.vol_history) < self.vol_len:
                continue

            vol_hi = max(self.vol_history) / 2.5
            vol_lo = min(self.vol_history) / 2.5

            atr = self.update_atr(prev, curr)
            if atr is None:
                continue

            width = atr * self.box_mult

            ph = self.pivot_high(data, i)
            pl = self.pivot_low(data, i)

            # ---------------- SUPPORT ----------------
            if pl and vol > vol_hi:
                self.support = pl
                self.support_zone = pl - width

            # ---------------- RESISTANCE ----------------
            if ph and vol < vol_lo:
                self.resistance = ph
                self.resistance_zone = ph + width

            # ---------------- SIGNALS ----------------
            if self.resistance and self.resistance_zone:
                # breakout resistance
                if curr["low"] > self.resistance_zone:
                    self.res_is_sup = True

                # resistance holds
                if curr["high"] < self.resistance:
                    signals.append({
                        "signal": "buyPE",
                        "type": "Res_Hold",
                        "price": curr["high"],
                        "time": curr["time"]
                    })

                # res -> support flip
                if self.res_is_sup:
                    signals.append({
                        "signal": "buyCE",
                        "type": "Res_to_Sup",
                        "price": curr["low"],
                        "time": curr["time"]
                    })

            if self.support and self.support_zone:
                # breakout support
                if curr["high"] < self.support_zone:
                    self.sup_is_res = True

                # support holds
                if curr["low"] > self.support:
                    signals.append({
                        "signal": "buyCE",
                        "type": "Sup_Hold",
                        "price": curr["low"],
                        "time": curr["time"]
                    })

                # sup -> resistance flip
                if self.sup_is_res:
                    signals.append({
                        "signal": "buyPE",
                        "type": "Sup_to_Res",
                        "price": curr["high"],
                        "time": curr["time"]
                    })

        return signals