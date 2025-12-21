import time
from math import sin, cos, sqrt, fabs, atan, radians, floor, pi, atan2, degrees, asin

LAT = 53.29756504536339  # Local defaults
LONG = -2.102811634540558

def now_days() -> int:
    secs_per_day = 86400
    t = RiSet.mtime()
    t -= t % secs_per_day
    return round(t / secs_per_day)

def quad(ym, yz, yp):
    nz = 0
    a = 0.5 * (ym + yp) - yz
    b = 0.5 * (yp - ym)
    c = yz
    if a == 0:
        return 0, 0, 0, 0
    xe = -b / (2 * a)
    ye = (a * xe + b) * xe + c
    dis = b * b - 4.0 * a * c
    if dis > 0:
        if b < 0:
            z2 = (-b + sqrt(dis)) / (2 * a)
        else:
            z2 = (-b - sqrt(dis)) / (2 * a)
        z1 = (c / a) / z2
        if fabs(z1) <= 1.0:
            nz += 1
        if fabs(z2) <= 1.0:
            nz += 1
        if z1 < -1.0:
            z1 = z2
        return nz, z1, z2, ye
    return 0, 0, 0, 0

def get_mjd(ndays: int = 0) -> int:
    secs_per_day = 86400
    days_from_epoch = now_days() + ndays
    mjepoch = 40587
    if time.gmtime(0)[0] == 2000:
        mjepoch += 10957
    return mjepoch + days_from_epoch

def frac(x):
    return x % 1

def to_int(x):
    return None if x is None else round(x)

def minisun(t):
    coseps = 0.9174805004
    sineps = 0.397780757938
    e = 0.0167
    m = 2 * pi * frac(0.993133 + 99.997361 * t)
    dl = 6893.0 * sin(m) + 72.0 * sin(2 * m)
    l = 2 * pi * frac(0.7859453 + m / (2 * pi) + (6191.2 * t + dl) / 1296000)
    sl = sin(l)
    x = cos(l)
    y = coseps * sl
    z = sineps * sl
    distance_AU = (1 - e**2) / (1 + e * cos(m))
    distance_km = distance_AU * 149597870.7
    return x, y, z, distance_km

def minimoon(t):
    arc = 206264.8062
    coseps = 0.9174805004
    sineps = 0.397780757938
    l0 = frac(0.606433 + 1336.855225 * t)
    l = 2 * pi * frac(0.374897 + 1325.552410 * t)
    ls = 2 * pi * frac(0.993133 + 99.997361 * t)
    d = 2 * pi * frac(0.827361 + 1236.853086 * t)
    f = 2 * pi * frac(0.259086 + 1342.227825 * t)
    dl = 22640 * sin(l)
    dl += -4586 * sin(l - 2 * d)
    dl += +2370 * sin(2 * d)
    dl += +769 * sin(2 * l)
    dl += -668 * sin(ls)
    dl += -412 * sin(2 * f)
    dl += -212 * sin(2 * l - 2 * d)
    dl += -206 * sin(l + ls - 2 * d)
    dl += +192 * sin(l + 2 * d)
    dl += -165 * sin(ls - 2 * d)
    dl += -125 * sin(d)
    dl += -110 * sin(l + ls)
    dl += +148 * sin(l - ls)
    dl += -55 * sin(2 * f - 2 * d)
    s = f + (dl + 412 * sin(2 * f) + 541 * sin(ls)) / arc
    h = f - 2 * d
    n = -526 * sin(h)
    n += +44 * sin(l + h)
    n += -31 * sin(-l + h)
    n += -23 * sin(ls + h)
    n += +11 * sin(-ls + h)
    n += -25 * sin(-2 * l + f)
    n += +21 * sin(-l + f)
    l_moon = 2 * pi * frac(l0 + dl / 1296000)
    b_moon = (18520.0 * sin(s) + n) / arc
    cb = cos(b_moon)
    x = cb * cos(l_moon)
    v = cb * sin(l_moon)
    w = sin(b_moon)
    y = coseps * v - sineps * w
    z = sineps * v + coseps * w
    distance_km = sqrt(x**2 + y**2 + z**2) * 384400
    return x, y, z, distance_km

def topocentric(x_geocentric, y_geocentric, z_geocentric, distance_km, lat_deg, lon_deg, lst_deg):
    Re_km = 6378.137
    φ = radians(lat_deg)
    H = radians(lst_deg)
    x_obs = cos(φ) * cos(H)
    y_obs = cos(φ) * sin(H)
    z_obs = sin(φ)
    rho = distance_km / Re_km
    xt = x_geocentric * rho - x_obs
    yt = y_geocentric * rho - y_obs
    zt = z_geocentric * rho - z_obs
    r = sqrt(xt**2 + yt**2 + zt**2)
    x_topocentric = xt / r
    y_topocentric = yt / r
    z_topocentric = zt / r
    return x_topocentric, y_topocentric, z_topocentric

class RiSet:
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

    def __init__(self, lat=LAT, long=LONG, lto=0, riset_deg = -0.833, tlight_deg=None, dst=lambda x: x):
        self.sglat = sin(radians(lat))
        self.cglat = cos(radians(lat))
        self.lat = lat
        self.long = long
        self.check_lto(lto)
        self.lto = round(lto * 3600)
        self.sinho_riset = sin(radians(riset_deg))
        self.tlight = sin(radians(tlight_deg)) if tlight_deg is not None else tlight_deg
        self.dst = dst
        self.mjd = None
        self._times = [None] * 6
        self.set_day()
        if RiSet.verbose:
            RiSet.verbose = False

    def set_day(self, day: int = 0, update_times = True):
        mjd = get_mjd(day)
        if not update_times:
            self.mjd = mjd
            self._times = [None] * 6
            return self
        if self.mjd is None or self.mjd != mjd:
            spd = 86400
            self._t0 = ((self.mtime() + day * spd) // spd) * spd
            self.update(mjd)
        return self

    def sunrise(self, variant: int = 0):
        return self._format(self._times[0], variant)

    def sunset(self, variant: int = 0):
        return self._format(self._times[1], variant)

    def moonrise(self, variant: int = 0):
        return self._format(self._times[2], variant)

    def moonset(self, variant: int = 0):
        return self._format(self._times[3], variant)

    def tstart(self, variant: int = 0):
        return self._format(self._times[4], variant)

    def tend(self, variant: int = 0):
        return self._format(self._times[5], variant)

    def set_lto(self, t):
        self.check_lto(t)
        self.lto = round(t * 3600)

    def has_risen(self, sun: bool):
        return self.has_x(True, sun)

    def has_set(self, sun: bool):
        return self.has_x(False, sun)

    def is_up(self, sun: bool):
        hr = self.has_risen(sun)
        hs = self.has_set(sun)
        rt = self.sunrise() if sun else self.moonrise()
        st = self.sunset() if sun else self.moonset()
        if rt is None and st is None:
            return self.above_horizon(sun)
        if not (hr ^ hs):
            if not ((rt is None) or (st is None)):
                return rt > st
        if not (hr or hs):
            return rt is None
        return hr and not hs

    def has_x(self, risen: bool, sun: bool):
        if risen:
            st = self.sunrise(1) if sun else self.moonrise(1)
        else:
            st = self.sunset(1) if sun else self.moonset(1)
        if st is not None:
            return st < self.dst(self.mtime())
        return False

    def above_horizon(self, sun: bool):
        now = self.mtime() + self.lto
        tutc = (now % 86400) / 3600
        return self.sin_alt(tutc, sun) > 0

    def update(self, mjd):
        for x in range(len(self._times)):
            self._times[x] = None
        days = (1, 2) if self.lto < 0 else (1,) if self.lto == 0 else (0, 1)
        tr = None
        ts = None
        for day in days:
            self.mjd = mjd + day - 1
            sr, ss = self.rise_set(True, False)
            if self.tlight is not None:
                tr, ts = self.rise_set(True, True)
            mr, ms = self.rise_set(False, False)
            self.adjust((sr, ss, mr, ms, tr, ts), day)
        self.mjd = mjd

    def adjust(self, times, day):
        for idx, n in enumerate(times):
            if n is not None:
                n += self.lto + (day - 1) * 86400
                n = self.dst(n)
                h = n // 3600
                if 0 <= h < 24:
                    self._times[idx] = n

    def _format(self, n, variant):
        if (n is not None) and (variant & 4):
            variant &= 0x03
            n = self.dst(n + self._t0) - self._t0
        if variant == 0:
            return n
        elif variant == 1:
            return None if n is None else n + self._t0
        if n is None:
            return "--:--:--"
        else:
            hr, tmp = divmod(n, 3600)
            mi, sec = divmod(tmp, 60)
            return f"{hr:02d}:{mi:02d}:{sec:02d}"

    def check_lto(self, t):
        if not -15 < t < 15:
            raise ValueError("Invalid local time offset.")

    def lstt(self, t, h):
        d = t * 36525
        df = frac(0.5 + h / 24)
        c1 = 360
        c2 = 0.98564736629
        dsum = c1 * df + c2 * d
        lst = 280.46061837 + dsum + t * t * (0.000387933 - t / 38710000)
        return lst

    def sin_alt(self, hour, sun):
        func = minisun if sun else minimoon
        mjd = (self.mjd - 51544.5) + hour / 24.0
        t = mjd / 36525.0
        x, y, z, distance_km = func(t)
        tl = self.lstt(t, hour) + self.long
        return self.sglat * z + self.cglat * (x * cos(radians(tl)) + y * sin(radians(tl)))

    def alt_az_ra_dec(self, hour, sun=True):
        func = minisun if sun else minimoon
        mjd = (self.mjd - 51544.5) + hour / 24.0
        t = mjd / 36525.0
        tl = self.lstt(t, hour) + self.long
        xg, yg, zg, distance_km = func(t)
        xt, yt, zt = topocentric(xg, yg, zg, distance_km, self.lat, self.long, tl)
        sin_alt = self.sglat * zt + self.cglat * (xt * cos(radians(tl)) + yt * sin(radians(tl)))
        alt = degrees(asin(sin_alt))
        rho = sqrt(xg * xg + yg * yg)
        dec = degrees(atan2(zg, rho))
        ra_base = xg + rho
        epsilon = 1e-9
        if abs(ra_base) < epsilon:
            ra_base = epsilon
        ra = ((48.0 / (2 * pi)) * atan(yg / ra_base)) % 24
        hourangle = radians(tl) - radians(ra * 15)
        hourangle_hours = (degrees(hourangle) % 360)  / 15.0
        sh = sin(hourangle)
        ch = cos(hourangle)
        sd = sin(radians(dec))
        cd = cos(radians(dec))
        sl = self.sglat
        cl = self.cglat
        x_az = -ch * cd * sl + sd * cl
        y_az = -sh * cd
        az = degrees(atan2(y_az, x_az)) % 360
        return alt, az, ra, dec

    def rise_set(self, sun, tl):
        t_rise = None
        t_set = None
        if tl:
            sinho = self.tlight
        else:
            sinho = self.sinho_riset
        yp = self.sin_alt(0, sun) - sinho
        for hour in range(1, 24, 2):
            ym = yp
            yz = self.sin_alt(hour, sun) - sinho
            yp = self.sin_alt(hour + 1, sun) - sinho
            nz, z1, z2, ye = quad(ym, yz, yp)
            if nz == 1:
                if ym < 0.0:
                    t_rise = 3600 * (hour + z1)
                else:
                    t_set = 3600 * (hour + z1)
            elif nz == 2:
                if ye < 0.0:
                    t_rise = 3600 * (hour + z2)
                    t_set = 3600 * (hour + z1)
                else:
                    t_rise = 3600 * (hour + z1)
                    t_set = 3600 * (hour + z2)

            if t_rise is not None and t_set is not None:
                break
        return to_int(t_rise), to_int(t_set)