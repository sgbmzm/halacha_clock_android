import time
import json
import math
from sun_moon_sgb import RiSet
from moonphase_sgb import MoonPhase
from mpy_heb_date import get_heb_date_and_holiday_from_greg_date, heb_weekday_names

# --- רשימת המיקומים עם איזורי זמן ---
# tz_id חייב להיות מזהה חוקי של IANA
LOCATIONS = [
    {'name': 'ירושלים', 'lat': 31.7768, 'long': 35.2357, 'alt': 750.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'בני ברק', 'lat': 32.0831, 'long': 34.8327, 'alt': 30.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'חיפה', 'lat': 32.8, 'long': 34.991, 'alt': 300.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'באר שבע', 'lat': 31.24, 'long': 34.79, 'alt': 280.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'תל אביב', 'lat': 32.08, 'long': 34.78, 'alt': 5.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'צפת', 'lat': 32.96, 'long': 35.49, 'alt': 850.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'אילת', 'lat': 29.55, 'long': 34.95, 'alt': 10.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'ניו יורק', 'lat': 40.71, 'long': -74.00, 'alt': 10.0, 'tz_id': 'America/New_York'},
    {'name': 'לונדון', 'lat': 51.50, 'long': -0.12, 'alt': 15.0, 'tz_id': 'Europe/London'},
    {'name': 'פריז', 'lat': 48.85, 'long': 2.35, 'alt': 35.0, 'tz_id': 'Europe/Paris'},
    {'name': 'טוקיו', 'lat': 35.67, 'long': 139.65, 'alt': 40.0, 'tz_id': 'Asia/Tokyo'},
]

def get_locations_list():
    return json.dumps([loc['name'] for loc in LOCATIONS])

def get_location_coords(index):
    if 0 <= index < len(LOCATIONS):
        return json.dumps(LOCATIONS[index])
    return json.dumps(LOCATIONS[0])

# --- פונקציות עזר (ללא שינוי מהותי, רק מוודאים שהן כאן) ---

def seconds_to_time_str(seconds):
    if seconds is None: return "--:--"
    seconds = seconds % 86400
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def calculate_temporal_time_from_seconds(current_seconds, sunrise_seconds, sunset_seconds):
    if sunrise_seconds is None or sunset_seconds is None: return "---", 0

    is_day = sunrise_seconds <= current_seconds < sunset_seconds

    if is_day:
        day_len = sunset_seconds - sunrise_seconds
        time_since = current_seconds - sunrise_seconds
    else:
        day_len = (24 * 3600) - (sunset_seconds - sunrise_seconds)
        if current_seconds >= sunset_seconds:
            time_since = current_seconds - sunset_seconds
        else:
            time_since = (24 * 3600 - sunset_seconds) + current_seconds

    if day_len == 0: return "---", 0

    sec_per_hour = day_len / 12

    h = int(time_since / sec_per_hour)
    remainder = time_since % sec_per_hour
    m = int((remainder / sec_per_hour) * 60)

    return f'{h:02d}:{m:02d}', sec_per_hour

def get_data_for_app(lat, long, altitude, utc_offset, mga_deg, sunrise_deg):
    # כאן utc_offset מגיע כבר מחושב נכון מהאנדרואיד לפי המיקום הנבחר
    timestamp = time.time()
    local_timestamp = timestamp + (utc_offset * 3600)
    tm = time.gmtime(local_timestamp)

    current_seconds_from_midnight = (tm.tm_hour * 3600) + (tm.tm_min * 60) + tm.tm_sec

    RiSet.set_time(local_timestamp)

    riset_gra = RiSet(lat, long, lto=utc_offset, riset_deg=sunrise_deg, tlight_deg=mga_deg)
    riset_other = RiSet(lat, long, lto=utc_offset, riset_deg=-4.61, tlight_deg=-10.5)

    sunrise = riset_gra.sunrise(0)
    sunset = riset_gra.sunset(0)
    mga_sunrise = riset_gra.tstart(0)
    mga_sunset = riset_gra.tend(0)

    misheyakir = riset_other.tstart(0)
    tzet_geanim = riset_other.sunset(0)

    current_hour_decimal = tm.tm_hour + tm.tm_min/60 + tm.tm_sec/3600
    s_alt, s_az, _, _ = riset_gra.alt_az_ra_dec(current_hour_decimal, sun=True)
    m_alt, m_az, _, _ = riset_gra.alt_az_ra_dec(current_hour_decimal, sun=False)

    MoonPhase.tim = round(local_timestamp)
    mp = MoonPhase()
    moon_percent = mp.phase() * 100

    is_after_sunset = sunset and current_seconds_from_midnight > sunset

    g_year, g_month, g_day = tm.tm_year, tm.tm_mon, tm.tm_mday
    if is_after_sunset:
        next_day_ts = local_timestamp + 86400
        ndt = time.gmtime(next_day_ts)
        g_year, g_month, g_day = ndt.tm_year, ndt.tm_mon, ndt.tm_mday

    heb_date_str, _, holiday_name, lite_holiday, is_rc = get_heb_date_and_holiday_from_greg_date(g_year, g_month, g_day)

    wday_map = {6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
    heb_wday_num = wday_map[tm.tm_wday]
    if is_after_sunset:
        heb_wday_num = (heb_wday_num % 7) + 1

    heb_wday_str = heb_weekday_names(heb_wday_num)
    full_heb_date = f"{heb_wday_str}, {heb_date_str}"
    if is_after_sunset: full_heb_date = "ליל " + full_heb_date

    bg_color_code = 0
    if heb_wday_num == 7 or holiday_name:
        bg_color_code = 2
    elif lite_holiday or is_rc:
        bg_color_code = 1
        if not holiday_name and lite_holiday: holiday_name = lite_holiday

    gra_time_str, sec_gra = calculate_temporal_time_from_seconds(current_seconds_from_midnight, sunrise, sunset)
    min_gra = round(sec_gra / 60, 1)

    mga_time_str, sec_mga = calculate_temporal_time_from_seconds(current_seconds_from_midnight, mga_sunrise, mga_sunset)
    min_mga = round(sec_mga / 60, 1)

    chatzot = None
    if sunrise is not None and sunset is not None:
        day_len = sunset - sunrise
        chatzot = sunrise + (day_len / 2)

    # עיגול אופסט לתצוגה יפה (למשל 2.0 יהפוך ל-2, אבל 5.5 יישאר 5.5)
    offset_display = int(utc_offset) if utc_offset.is_integer() else utc_offset

    data = {
        "time": f"{tm.tm_hour:02d}:{tm.tm_min:02d}:{tm.tm_sec:02d}",
        "utc_offset_str": f"UTC{'+' if utc_offset >=0 else ''}{offset_display}",
        "date_greg": f"{tm.tm_mday}/{tm.tm_mon}/{tm.tm_year}",

        "heb_date": full_heb_date,
        "holiday": holiday_name if holiday_name else "",
        "bg_color_code": bg_color_code,

        "location_info": {
            "lat": f"{lat:.4f}",
            "long": f"{long:.4f}",
            "alt": f"{altitude:.0f}m"
        },

        "sun": {
            "alt": f"{s_alt:.2f}",
            "az": f"{s_az:.1f}"
        },
        "moon": {
            "alt": f"{m_alt:.2f}",
            "az": f"{m_az:.1f}",
            "percent": f"{moon_percent:.1f}%"
        },

        "zmanim_clocks": {
            "gra_clock": gra_time_str,
            "gra_min": str(min_gra),
            "mga_clock": mga_time_str,
            "mga_min": str(min_mga),
            "gra_def": f"הנץ {seconds_to_time_str(sunrise)} - שקיעה {seconds_to_time_str(sunset)}" if sunrise else "",
            "mga_def": f"עלות {seconds_to_time_str(mga_sunrise)} - צאת {seconds_to_time_str(mga_sunset)}" if mga_sunrise else ""
        },

        "times_list": [
            f"עלות ({mga_deg}°): {seconds_to_time_str(mga_sunrise)}",
            f"משיכיר (-10.5°): {seconds_to_time_str(misheyakir)}",
            f"הנץ החמה: {seconds_to_time_str(sunrise)}",
            f"חצות היום: {seconds_to_time_str(chatzot)}",
            f"שקיעה: {seconds_to_time_str(sunset)}",
            f"צאת (-4.61°): {seconds_to_time_str(tzet_geanim)}"
        ]
    }
    
    return json.dumps(data)