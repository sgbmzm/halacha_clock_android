package iam699030.gmail.jewishcalendarclock

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.WindowManager
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.util.TimeZone
import kotlin.math.roundToInt

class MainActivity : AppCompatActivity(), LocationListener {

    private lateinit var tvLocationName: TextView
    private lateinit var tvCoords: TextView
    private lateinit var tvTime: TextView
    private lateinit var tvDate: TextView
    private lateinit var tvUtc: TextView
    private lateinit var tvHebDate: TextView
    private lateinit var tvHoliday: TextView

    // שעונים
    private lateinit var tvGraClock: TextView
    private lateinit var tvMgaClock: TextView
    private lateinit var tvGraMin: TextView
    private lateinit var tvMgaMin: TextView
    private lateinit var tvGraDef: TextView
    private lateinit var tvMgaDef: TextView

    // שמש ירח
    private lateinit var tvSunAlt: TextView
    private lateinit var tvSunAz: TextView
    private lateinit var tvMoonAlt: TextView
    private lateinit var tvMoonAz: TextView
    private lateinit var tvMoonPercent: TextView

    private lateinit var tvZmanimList: TextView

    private val handler = Handler(Looper.getMainLooper())
    private lateinit var pythonModule: com.chaquo.python.PyObject
    private var locationManager: LocationManager? = null

    // נתונים לחישוב
    private var currentLat = 31.7768
    private var currentLong = 35.2357
    private var currentAlt = 750.0
    private var currentLocationName = "ירושלים (רשימה)"

    // משתנה לשמירת ה-ID של איזור הזמן (למשל "America/New_York")
    private var currentTimeZoneId = "Asia/Jerusalem"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvLocationName = findViewById(R.id.tvLocationName)
        tvCoords = findViewById(R.id.tvCoords)
        tvTime = findViewById(R.id.tvMainTime)
        tvUtc = findViewById(R.id.tvUtcOffset)
        tvDate = findViewById(R.id.tvGregDate)
        tvHebDate = findViewById(R.id.tvHebDate)
        tvHoliday = findViewById(R.id.tvHoliday)

        tvGraClock = findViewById(R.id.tvGraClock)
        tvMgaClock = findViewById(R.id.tvMgaClock)
        tvGraMin = findViewById(R.id.tvGraMin)
        tvMgaMin = findViewById(R.id.tvMgaMin)
        tvGraDef = findViewById(R.id.tvGraDef)
        tvMgaDef = findViewById(R.id.tvMgaDef)

        tvSunAlt = findViewById(R.id.tvSunAlt)
        tvSunAz = findViewById(R.id.tvSunAz)
        tvMoonAlt = findViewById(R.id.tvMoonAlt)
        tvMoonAz = findViewById(R.id.tvMoonAz)
        tvMoonPercent = findViewById(R.id.tvMoonPercent)

        tvZmanimList = findViewById(R.id.tvZmanimList)

        findViewById<ImageView>(R.id.btnSettings).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        initPython()
        locationManager = getSystemService(LOCATION_SERVICE) as LocationManager
    }

    override fun onResume() {
        super.onResume()
        loadPreferences()
        startClockLoop()
    }

    override fun onPause() {
        super.onPause()
        handler.removeCallbacksAndMessages(null)
        locationManager?.removeUpdates(this)
    }

    private fun initPython() {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()
        pythonModule = py.getModule("logic_api")
    }

    private fun loadPreferences() {
        val prefs = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
        val isGps = prefs.getBoolean("is_gps", false)
        val keepScreen = prefs.getBoolean("keep_screen", true)

        if (keepScreen) {
            window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        } else {
            window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        }

        if (isGps) {
            startGps()
            currentLocationName = "GPS (מחפש...)"
            // ב-GPS אנחנו מניחים שהמשתמש נמצא פיזית במקום, אז משתמשים בשעון המכשיר
            currentTimeZoneId = TimeZone.getDefault().id
        } else {
            locationManager?.removeUpdates(this)
            val index = prefs.getInt("location_index", 0)

            // שליפת המידע כולל timezone id מהפייתון
            val locDataStr = pythonModule.callAttr("get_location_coords", index).toString()
            val locJson = JSONObject(locDataStr)

            currentLat = locJson.getDouble("lat")
            currentLong = locJson.getDouble("long")
            currentAlt = locJson.getDouble("alt")
            // כאן התיקון: שליפת ה-ID מתוך ה-JSON
            // אם במקרה אין בקובץ (כמו ברשימה ישנה), ברירת מחדל ירושלים
            currentTimeZoneId = locJson.optString("tz_id", "Asia/Jerusalem")

            currentLocationName = locJson.getString("name") + " (רשימה)"
        }
    }

    private fun startGps() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), 1)
            return
        }
        locationManager?.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000L, 100f, this)
        val lastLoc = locationManager?.getLastKnownLocation(LocationManager.GPS_PROVIDER)
        if (lastLoc != null) {
            onLocationChanged(lastLoc)
        }
    }

    override fun onLocationChanged(loc: Location) {
        currentLat = loc.latitude
        currentLong = loc.longitude
        currentAlt = loc.altitude
        currentLocationName = "GPS (פעיל)"
        // עדכון איזור הזמן שיהיה תואם למכשיר (כי המשתמש ב-GPS)
        currentTimeZoneId = TimeZone.getDefault().id
    }

    private fun startClockLoop() {
        val runnable = object : Runnable {
            override fun run() {
                updateData()
                handler.postDelayed(this, 1000)
            }
        }
        handler.post(runnable)
    }

    private fun updateData() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val prefs = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
                val mgaDeg = prefs.getFloat("mga_deg", -16f)
                val sunDeg = prefs.getFloat("sun_deg", -0.833f)

                // חישוב UTC Offset מדויק לפי המיקום שנבחר!
                val targetTimeZone = TimeZone.getTimeZone(currentTimeZoneId)
                val offsetMillis = targetTimeZone.getOffset(System.currentTimeMillis())
                val offsetHours = offsetMillis / 3600000.0

                // שליחה לפייתון עם ה-Offset הנכון של המיקום
                val jsonResultStr = pythonModule.callAttr(
                    "get_data_for_app",
                    currentLat, currentLong, currentAlt, offsetHours, mgaDeg, sunDeg
                ).toString()

                withContext(Dispatchers.Main) {
                    parseAndDisplay(jsonResultStr)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun parseAndDisplay(jsonStr: String) {
        val data = JSONObject(jsonStr)

        tvLocationName.text = currentLocationName
        tvDate.text = data.getString("date_greg")
        tvTime.text = data.getString("time")
        tvUtc.text = data.getString("utc_offset_str")

        val locInfo = data.getJSONObject("location_info")
        tvCoords.text = "Lat: ${locInfo.getString("lat")}  Long: ${locInfo.getString("long")}  Alt: ${locInfo.getString("alt")}"

        tvHebDate.text = data.getString("heb_date")
        val colorCode = data.getInt("bg_color_code")
        tvHebDate.setBackgroundColor(when(colorCode) {
            2 -> Color.YELLOW
            1 -> Color.parseColor("#00BCD4")
            else -> Color.parseColor("#333333")
        })
        tvHebDate.setTextColor(if(colorCode == 2) Color.BLACK else if (colorCode == 1) Color.BLACK else Color.CYAN)
        tvHoliday.text = data.getString("holiday")

        val clocks = data.getJSONObject("zmanim_clocks")
        tvGraClock.text = clocks.getString("gra_clock")
        tvGraMin.text = "${clocks.getString("gra_min")} דק'"
        tvGraDef.text = clocks.getString("gra_def")

        tvMgaClock.text = clocks.getString("mga_clock")
        tvMgaMin.text = "${clocks.getString("mga_min")} דק'"
        tvMgaDef.text = clocks.getString("mga_def")

        val sun = data.getJSONObject("sun")
        tvSunAlt.text = "${sun.getString("alt")}°"
        tvSunAz.text = "${sun.getString("az")}°"

        val moon = data.getJSONObject("moon")
        tvMoonAlt.text = "${moon.getString("alt")}°"
        tvMoonAz.text = "${moon.getString("az")}°"
        tvMoonPercent.text = "${moon.getString("percent")}"

        val timesList = data.getJSONArray("times_list")
        val sb = StringBuilder()
        for (i in 0 until timesList.length()) {
            sb.append(timesList.getString(i)).append("\n")
        }
        tvZmanimList.text = sb.toString()
    }
}
