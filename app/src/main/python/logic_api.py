import time
import json
import math
from sun_moon_sgb import RiSet
from moonphase_sgb import MoonPhase
from mpy_heb_date import get_heb_date_and_holiday_from_greg_date, heb_weekday_names

# --- רשימת המיקומים עם איזורי זמן ---
# tz_id חייב להיות מזהה חוקי של IANA
'''
LOCATIONS = [
    {'name': 'ירושלים', 'lat': 31.7768, 'long': 35.2357, 'alt': 750.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'מודיעין עילית', 'lat': 31.940826, 'long': 35.037057, 'alt': 320.0, 'tz_id': 'Asia/Jerusalem'},
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
'''
LOCATIONS = [
    {'name': 'משווה-0-0', 'lat': 0.0, 'long': 0.0, 'alt': 0.0, 'tz_id': 'Etc/UTC'},
    {'name': 'קו-המשווה', 'lat': 0.0, 'long': 0.0, 'alt': 0.0, 'tz_id': 'Etc/UTC'},
    {'name': 'הקוטב-הצפוני', 'lat': 90.0, 'long': 0.0, 'alt': 0.0, 'tz_id': 'Etc/UTC'},

    {'name': 'ניו יורק', 'lat': 40.7143528, 'long': -74.0059731, 'alt': 9.8, 'tz_id': 'America/New_York'},
    {'name': 'אופקים', 'lat': 31.309, 'long': 34.61, 'alt': 170.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'אילת', 'lat': 29.55, 'long': 34.95, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'אלעד', 'lat': 32.05, 'long': 34.95, 'alt': 150.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'אריאל', 'lat': 32.10, 'long': 35.17, 'alt': 521.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'אשדוד', 'lat': 31.79, 'long': 34.641, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'אשקלון', 'lat': 31.65, 'long': 34.56, 'alt': 60.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'באר שבע', 'lat': 31.24, 'long': 34.79, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'בית שאן', 'lat': 32.5, 'long': 35.5, 'alt': -120.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'בית שמש', 'lat': 31.74, 'long': 34.98, 'alt': 300.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'ביתר עילית', 'lat': 31.69, 'long': 35.12, 'alt': 800.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'בני ברק', 'lat': 32.083156, 'long': 34.832722, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'דימונה', 'lat': 31.07, 'long': 35.03, 'alt': 570.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'הרצליה', 'lat': 32.16, 'long': 34.84, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'זכרון יעקב', 'lat': 32.57, 'long': 34.95, 'alt': 170.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'חדרה', 'lat': 32.43, 'long': 34.92, 'alt': 53.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'חיפה', 'lat': 32.8, 'long': 34.991, 'alt': 300.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'טבריה', 'lat': 32.79, 'long': 35.531, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'ירושלים', 'lat': 31.776812, 'long': 35.235694, 'alt': 750.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'כרמיאל', 'lat': 32.915, 'long': 35.292, 'alt': 315.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'לוד', 'lat': 31.95, 'long': 34.89, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'מודיעין עילית', 'lat': 31.940826, 'long': 35.037057, 'alt': 320.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'מצפה רמון', 'lat': 30.6097894, 'long': 34.8120107, 'alt': 855.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'נהריה', 'lat': 33.01, 'long': 35.1, 'alt': 25.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'נתיבות', 'lat': 31.42, 'long': 34.59, 'alt': 142.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'נתניה', 'lat': 32.34, 'long': 34.86, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'עכו', 'lat': 32.93, 'long': 35.08, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'עפולה', 'lat': 32.6, 'long': 35.29, 'alt': 60.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'ערד', 'lat': 31.26, 'long': 35.21, 'alt': 640.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'פתח תקווה', 'lat': 32.09, 'long': 34.88, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'צפת', 'lat': 32.962, 'long': 35.496, 'alt': 850.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'קרית גת', 'lat': 31.61, 'long': 34.77, 'alt': 159.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'קרית שמונה', 'lat': 33.2, 'long': 35.56, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'ראשון לציון', 'lat': 31.96, 'long': 34.8, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'רחובות', 'lat': 31.89, 'long': 34.81, 'alt': 76.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'רמלה', 'lat': 31.92, 'long': 34.86, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'רעננה', 'lat': 32.16, 'long': 34.85, 'alt': 71.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'שדרות', 'lat': 31.52, 'long': 34.59, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},
    {'name': 'תל אביב', 'lat': 32.01, 'long': 34.75, 'alt': 0.0, 'tz_id': 'Asia/Jerusalem'},

    {'name': 'אומן', 'lat': 48.74732, 'long': 30.23332, 'alt': 211.0, 'tz_id': 'Europe/Kyiv'},
    {'name': 'אמסטרדם', 'lat': 52.38108, 'long': 4.88845, 'alt': 15.0, 'tz_id': 'Europe/Amsterdam'},
    {'name': 'וילנה', 'lat': 54.672298, 'long': 25.2697, 'alt': 112.0, 'tz_id': 'Europe/Vilnius'},
    {'name': 'לונדון', 'lat': 51.5001524, 'long': -0.1262362, 'alt': 14.6, 'tz_id': 'Europe/London'},
    {'name': 'מוסקווה', 'lat': 55.755786, 'long': 37.617633, 'alt': 151.0, 'tz_id': 'Europe/Moscow'},
    {'name': 'סטוקהולם', 'lat': 59.33, 'long': 18.06, 'alt': 28.0, 'tz_id': 'Europe/Stockholm'},
    {'name': 'פראג', 'lat': 50.0878114, 'long': 14.4204598, 'alt': 191.0, 'tz_id': 'Europe/Prague'},
    {'name': 'פריז', 'lat': 48.8566667, 'long': 2.3509871, 'alt': 35.0, 'tz_id': 'Europe/Paris'},
    {'name': 'פרנקפורט', 'lat': 50.1115118, 'long': 8.6805059, 'alt': 106.0, 'tz_id': 'Europe/Berlin'},
    {'name': 'קהיר', 'lat': 30.00022, 'long': 31.231873, 'alt': 23.0, 'tz_id': 'Africa/Cairo'},
    {'name': 'רומא', 'lat': 41.8954656, 'long': 12.4823243, 'alt': 20.0, 'tz_id': 'Europe/Rome'},
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
    s = int((((remainder / sec_per_hour) * 60) - m) * 60)

    return f'{h:02d}:{m:02d}:{s:02d}', sec_per_hour

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

    current_hour_decimal = (tm.tm_hour + tm.tm_min/60 + tm.tm_sec/3600) - utc_offset # כאן חובה להוריד את הפרש השעות
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
    if is_after_sunset: full_heb_date = "ליל: " + full_heb_date

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
            "alt": f"{s_alt:.3f}",
            "az": f"{s_az:.2f}"
        },
        "moon": {
            "alt": f"{m_alt:.3f}",
            "az": f"{m_az:.2f}",
            "percent": f"{moon_percent:.1f}%"
        },

        "zmanim_clocks": {
            "gra_clock": gra_time_str,
            "gra_min": str(min_gra),
            "mga_clock": mga_time_str,
            "mga_min": str(min_mga),
            "gra_def": f"הנץ ({sunrise_deg:.3f}°): {seconds_to_time_str(sunrise)}\nשקיעה ({sunrise_deg:.3f}°): {seconds_to_time_str(sunset)}" if sunrise else "",
            "mga_def": f"עלות השחר ({mga_deg}°): {seconds_to_time_str(mga_sunrise)}\nצאה''כ דר''ת ({mga_deg}°): {seconds_to_time_str(mga_sunset)}" if mga_sunrise else ""
        },

        "times_list": [
            f"עלות השחר({mga_deg}°): {seconds_to_time_str(mga_sunrise)}",
            f"משיכיר (-10.5°): {seconds_to_time_str(misheyakir)}",
            f"הנץ החמה: {seconds_to_time_str(sunrise)}",
            f"חצות היום: {seconds_to_time_str(chatzot)}",
            f"שקיעה: {seconds_to_time_str(sunset)}",
            f"צאת (-4.61°): {seconds_to_time_str(tzet_geanim)}"
        ]
    }
    
    return json.dumps(data)
