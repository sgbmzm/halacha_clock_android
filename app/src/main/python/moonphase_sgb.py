from math import radians, sin, cos, floor
import time
import array

SYNMONTH = 29.53058868

def meanphase(sdate: float, k: int) -> float:
    t = sdate / 36525
    t2 = t * t
    t3 = t2 * t
    nt1 = 0.75933 + SYNMONTH * k + 0.0001178 * t2 - 0.000000155 * t3
    return nt1 + 0.00033 * sin(radians(166.56 + 132.87 * t - 0.009173 * t2))

def truephase(k: int, phi: int) -> int:
    k += (0, 0.25, 0.5, 0.75)[phi]
    t = k / 1236.85
    t2 = t * t
    t3 = t2 * t
    m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3
    mprime = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3
    if phi in (0, 2):
        pt = (0.1734 - 0.000393 * t) * sin(radians(m))
        pt += 0.0021 * sin(radians(2 * m))
        pt -= 0.4068 * sin(radians(mprime))
        pt += 0.0161 * sin(radians(2 * mprime))
        pt -= 0.0004 * sin(radians(3 * mprime))
        pt += 0.0104 * sin(radians(2 * f))
        pt -= 0.0051 * sin(radians(m + mprime))
        pt -= 0.0074 * sin(radians(m - mprime))
        pt += 0.0004 * sin(radians(2 * f + m))
        pt -= 0.0004 * sin(radians(2 * f - m))
        pt -= 0.0006 * sin(radians(2 * f + mprime))
        pt += 0.0010 * sin(radians(2 * f - mprime))
        pt += 0.0005 * sin(radians(m + 2 * mprime))
    else:
        pt = (0.1721 - 0.0004 * t) * sin(radians(m))
        pt += 0.0021 * sin(radians(2 * m))
        pt -= 0.6280 * sin(radians(mprime))
        pt += 0.0089 * sin(radians(2 * mprime))
        pt -= 0.0004 * sin(radians(3 * mprime))
        pt += 0.0079 * sin(radians(2 * f))
        pt -= 0.0119 * sin(radians(m + mprime))
        pt -= 0.0047 * sin(radians(m - mprime))
        pt += 0.0003 * sin(radians(2 * f + m))
        pt -= 0.0004 * sin(radians(2 * f - m))
        pt -= 0.0006 * sin(radians(2 * f + mprime))
        pt += 0.0021 * sin(radians(2 * f - mprime))
        pt += 0.0003 * sin(radians(m + 2 * mprime))
        pt += 0.0004 * sin(radians(m - 2 * mprime))
        pt -= 0.0003 * sin(radians(2 * m + mprime))
        if phi < 2:
            pt += 0.0028 - 0.0004 * cos(radians(m)) + 0.0003 * cos(radians(mprime))
        else:
            pt += -0.0028 + 0.0004 * cos(radians(m)) - 0.0003 * cos(radians(mprime))
    pt = round(pt * 86400)
    pt += round(2_953_058_868 * 864 * k) // 1000_000
    qq = 0.0001178 * t2 - 0.000000155 * t3
    qq += 0.00033 * sin(radians(166.56 + 132.87 * t - 0.009173 * t2))
    pt += round(qq * 86400)
    return pt + 208_657_793_606

def dt_to_text(tim):
    t = time.localtime(tim)
    return f"{t[2]:02}/{t[1]:02}/{t[0]:4} {t[3]:02}:{t[4]:02}:{t[5]:02}"

class MoonPhase:
    verbose = True
    tim = None

    @classmethod
    def mtime(cls):
        return round(time.time()) if cls.tim is None else cls.tim
    
    @classmethod
    def set_time(cls, t):
        if time.gmtime(0)[0] == 2000:
            t -= 10957 * 86400
        cls.tim = t
    
    def __init__(self, lto: float = 0, dst=lambda x: x):
        self.lto_s = self._check_lto(lto)
        self.dst = dst
        self.phases = array.array("q", (0,) * 5)
        jepoch = 244058750
        if time.gmtime(0)[0] == 2000:
            jepoch += 1095700
        jepoch *= 864
        self.jepoch = jepoch
        self.secs = 0
        self.set_day()
        if MoonPhase.verbose:
            MoonPhase.verbose = False

    def _midnight(self, doff: float = 0):
        tl = round((self.mtime() // 86400 + doff) * 86400)
        return tl - self.lto_s

    def set_lto(self, t: float):
        self.lto_s = self._check_lto(t)

    def set_day(self, doff: float = 0):
        self.secs = round(self.mtime() + doff * 86400 - self.lto_s)
        start = self._midnight(doff)
        self._populate(start)

    def datum(self, text: bool = True):
        t = self.secs + self.lto_s
        return dt_to_text(t) if text else t

    def quarter(self, q: int, text: bool = True):
        if not 0 <= q <= 4:
            raise ValueError("Quarter nos must be from 0 to 4.")
        tutc = self.phases[q]
        t = self.dst(tutc + self.lto_s)
        return dt_to_text(t) if text else t

    def phase(self) -> float:
        t = self.secs
        if not (self.phases[0] <= t <= self.phases[4]):
            self.set_day()
        prev = self.phases[0]
        for n, phi in enumerate(self.phases):
            if phi > t:
                break
            prev = phi
        if prev == phi:
            r = (t - prev) * 0.25 / 637860.715488
            if r < 0:
                r = 1 - r
        else:
            r = (n - 1) * 0.25 + (t - prev) * 0.25 / (phi - prev)
        return min(r, 0.999999)

    def _next_lunation(self):
        self._populate(round(self.phases[2] + SYNMONTH * 86400))

    def nextphase(self, text: bool = True):
        n = 0
        lun = 0
        while True:
            yield n, lun, self.quarter(n, text)
            n += 1
            n %= 4
            if n == 0:
                self._next_lunation()
                lun += 1

    def _check_lto(self, lto: float) -> int:
        if not -15 < lto < 15:
            raise ValueError("Invalid local time offset.")
        return round(lto * 3600)

    def _populate(self, t: int):
        if self.phases[0] < t < self.phases[4]:
            return
        def jd1900(t: int) -> float:
            y, m, mday = time.localtime(t)[:3]
            if m <= 2:
                m += 12
                y -= 1
            b = round(y / 400 - y / 100 + y / 4)
            mjm = 365 * y - 679004 + b + int(30.6001 * (m + 1)) + mday
            return mjm - 15019.5

        sdate: float = jd1900(t)
        adate: float = sdate - 45
        yy, mm, dd = time.localtime(t)[:3]
        k1: int = floor((yy + ((mm - 1) * (1.0 / 12.0)) - 1900) * 12.3685)
        adate = meanphase(adate, k1)
        nt1: float = adate
        while True:
            adate += SYNMONTH
            k2: int = k1 + 1
            nt2: float = meanphase(adate, k2)
            if nt1 <= sdate and nt2 > sdate:
                break
            nt1 = nt2
            k1 = k2
        for n, k in enumerate((k1, k1, k1, k1, k2)):
            phi: int = truephase(k, n % 4)
            self.phases[n] = phi - self.jepoch