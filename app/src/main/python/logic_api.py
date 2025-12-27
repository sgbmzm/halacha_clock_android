import time
import json
import math
from math import sin, cos, tan, radians, degrees
from sun_moon_sgb import RiSet
from moonphase_sgb import MoonPhase
from mpy_heb_date import get_heb_date_and_holiday_from_greg_date, heb_weekday_names


# --- רשימת המיקומים עם איזורי זמן ---
# tz_id חייב להיות מזהה חוקי של IANA

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


# פונקצייה שמקבלת זמן כחותמן זמן ומחזירה את משוואת הזמן בדקות ליום זה
# לפי Meeus, בקירוב מצוין לשנים 2000–2100
# נבנתה על ידי צאט גיפיטי
def get_equation_of_time_from_timestamp(timestamp_input):
    
    # פונקצייה לקבלת זמן באלפי שנים מאז J2000.0 וגם יום יוליאני לצורך חישובים אסטרונומיים
    def get_julian_centuries_since_J2000_and_jd(timestamp):
        JD = timestamp / 86400.0 + 2440587.5
        JC = (JD - 2451545.0) / 36525.0
        return JC, JD
    
    # קבלת זמן באלפי שנים מאז J2000.0 לצורך החישובים, באמצעות הפונקצייה הנל
    T, JD = get_julian_centuries_since_J2000_and_jd(timestamp_input)

    # ואז ממשיכים כמו קודם:
    L0 = radians((280.46646 + 36000.76983 * T) % 360)
    e = 0.016708634 - 0.000042037 * T
    M = radians((357.52911 + 35999.05029 * T) % 360)
    y = tan(radians(23.439291 - 0.0130042 * T) / 2)
    y *= y
    equation_of_time_minutes = 4 * degrees(
        y * sin(2 * L0)
        - 2 * e * sin(M)
        + 4 * e * y * sin(M) * cos(2 * L0)
        - 0.5 * y * y * sin(4 * L0)
        - 1.25 * e * e * sin(2 * M)
    )
    
    equation_of_time_seconds = equation_of_time_minutes * 60
    
    return equation_of_time_seconds

# פונקצייה לקבלת הפרש השעות המקומי מגריניץ בלי התחשבות בשעון קיץ
# יש אפשרות להגדיר טרו או פאלס האם זה שעון קיץ או לא. כברירת מחדל זה לא
# אפשר להגדיר האם רוצים את ההפרש בשעות או בשניות וברירת המחדל היא בשעות
def get_generic_utc_offset(longitude_degrees, dst=False, in_seconds = False):
    offset = abs(round(longitude_degrees/15)) % 24
    offset = -offset if longitude_degrees < 0 else offset
    offset = offset + 1 if dst else offset
    return offset * 3600 if in_seconds else offset

# פונקצייה להמרת זמן מ-שניות ל- סטרינג שעות דקות ושניות, או רק ל- סטרינג דקות ושניות שבניתי בסיוע רובי הבוט
def convert_seconds(seconds, to_hours=False):
    # המרה לערך מוחלט כדי לא להחזיר סימן מינוס
    seconds = abs(seconds)
    # חישוב מספר הדקות והשניות שיש בשעה אחת, והדפסתם בפורמט של דקות ושניות
    if to_hours:
        return f'{seconds // 3600 :02.0f}:{(seconds % 3600) // 60 :02.0f}:{seconds % 60 :02.0f}'
    else:
        return f'{seconds // 60 :02.0f}:{seconds % 60 :02.0f}'

# פונקצייה לחישוב זמן מקומי (לפי חצות שנתי ממוצע שהוא בשעה 12), לפי קו האורך הגיאוגרפי האמיתי 
def LMT_LST_EOT(utc_timestamp, longitude_degrees, LST_EOT = True):
    offset_seconds = int(240 * longitude_degrees)  # 4 דקות לכל מעלה
    lmt_seconds = int(utc_timestamp) + offset_seconds # חייבים לעשות אינט למנוע שגיאות במיקרופייתון
    lmt_tuple = time.gmtime(int(lmt_seconds))   # לא מוסיף הטיה מקומית
    local_mean_time_string = seconds_to_time_str(int(lmt_seconds))
    ####################################################################
    if LST_EOT:
        equation_of_time_seconds = get_equation_of_time_from_timestamp(utc_timestamp)
        lst_seconds = lmt_seconds + int(equation_of_time_seconds) # חייבים לעשות אינט למנוע שגיאות במיקרופייתון
        lst_tuple = time.gmtime(int(lst_seconds))
        local_solar_time_string = seconds_to_time_str(int(lst_seconds))
        equation_of_time_string = f"{'+' if equation_of_time_seconds >0 else '-'}{convert_seconds(equation_of_time_seconds)}"
    else:
        local_solar_time_string, equation_of_time_string = "None","None"
    return local_mean_time_string, local_solar_time_string, equation_of_time_string



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

    
    sozkash_gra = None
    sozat_gra = None
    chatzot = None
    mincha_gedola = None
    mincha_ketana = None
    pelag_hamincha = None
    if sunrise is not None and sunset is not None:
        day_len = sunset - sunrise
        sozkash_gra = sunrise + ((day_len / 12) * 3)
        sozat_gra = sunrise + ((day_len / 12) * 4)
        chatzot = sunrise + ((day_len / 12) * 6)
        mincha_gedola = sunrise + ((day_len / 12) * 6.5)
        mincha_ketana = sunrise + ((day_len / 12) * 9.5)
        pelag_hamincha = sunrise + ((day_len / 12) * 10.45)
    
    sozkash_mga = None
    sozat_mga = None
    if mga_sunrise is not None and mga_sunset is not None:
        mga_day_len = mga_sunset - mga_sunrise
        sozkash_mga = mga_sunrise + ((mga_day_len / 12) * 3)
        sozat_mga = mga_sunrise + ((mga_day_len / 12) * 4)

    # עיגול אופסט לתצוגה יפה (למשל 2.0 יהפוך ל-2, אבל 5.5 יישאר 5.5)
    offset_display = int(utc_offset) if utc_offset.is_integer() else utc_offset
    
    # חישוב זמן שעבר מהשקיעה האחרונה.
    # מ 12 בלילה עד השקיעה מחשבים את השקיעה של אתמול לפי השקיעה של היום פחות 24 שעות וזה לא מדוייק אבל זה רק זמני
    seconds_since_last_sunset = current_seconds_from_midnight - sunset if current_seconds_from_midnight >= sunset else (24 * 3600 - sunset) + current_seconds_from_midnight
    ########### 2. שעון מקומי ממוצע, שעון מקומי שמשי אמיתי שחצות תמיד ב 12:00, ומשוואת הזמן  
    local_mean_time_string, local_solar_time_string, equation_of_time_string = LMT_LST_EOT(timestamp, long) # חייב לקבל זמן utc ולא מקומי
   

    data = {
        "time": f"{tm.tm_hour:02d}:{tm.tm_min:02d}:{tm.tm_sec:02d}",
        "gmt_time": seconds_to_time_str(timestamp),
        "lst_time": local_solar_time_string,
        "lmt_time": local_mean_time_string,
        "magrab_time": seconds_to_time_str(seconds_since_last_sunset),
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
            "percent": f"{moon_percent:.2f}%"
        },

        "zmanim_clocks": {
            "gra_clock": gra_time_str,
            "gra_min": str(min_gra),
            "mga_clock": mga_time_str,
            "mga_min": str(min_mga),
            "gra_def": f"זריחה: {seconds_to_time_str(sunrise)}\nשקיעה: {seconds_to_time_str(sunset)}" if sunrise else "",
            "mga_def": f"עלות השחר: {seconds_to_time_str(mga_sunrise)}\nצאה''כ דר''ת: {seconds_to_time_str(mga_sunset)}" if mga_sunrise else ""
        },

        "times_list": [
            "שעון ההלכה לאנדרואיד פותח בזכות מפתח המכנה עצמו בשם ''איש אמת'', שנדבה רוחו להקים את ההקמה הראשונית של אפליקציה זו",
            "",
            "שעון ההלכה לאנדרואיד מבית ''כוכבים וזמנים''",
            "sgbmzm@gmail.com",
            "",
            "להלן זמנים בשעון רגיל",
            "שימו לב! דיוק הזמנים הללו סוטה בכדקה",
            "",
            f"עלות השחר ({mga_deg}°): {seconds_to_time_str(mga_sunrise)}",
            f"משיכיר (-10.5°): {seconds_to_time_str(misheyakir)}",
            f"זריחה ({sunrise_deg:.3f}°): {seconds_to_time_str(sunrise)}",
            
            f"סוף שמע מג''א ({mga_deg}°): {seconds_to_time_str(sozkash_mga)}",
            f"סוף שמע גר''א ({sunrise_deg:.3f}°): {seconds_to_time_str(sozkash_gra)}",
            
            f"סוף תפילה מג''א ({mga_deg}°): {seconds_to_time_str(sozat_mga)}",
            f"סוף תפילה גר''א ({sunrise_deg:.3f}°): {seconds_to_time_str(sozat_gra)}",
            
            f"חצות היום: {seconds_to_time_str(chatzot)}",
            
            f"מנחה גדולה: {seconds_to_time_str(mincha_gedola)}",
            f"מנחה קטנה: {seconds_to_time_str(mincha_ketana)}",
            f"פלג המנחה: {seconds_to_time_str(pelag_hamincha)}",
            
            f"שקיעה ({sunrise_deg:.3f}°): {seconds_to_time_str(sunset)}",
            
            f"צאת דהגאונים (-4.61°): {seconds_to_time_str(tzet_geanim)}",
            f"צאת דר''ת ({mga_deg}°): {seconds_to_time_str(mga_sunset)}",
        ]
    }
    
    return json.dumps(data)
