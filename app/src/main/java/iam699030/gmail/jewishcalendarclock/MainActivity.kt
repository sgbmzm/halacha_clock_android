package iam699030.gmail.jewishcalendarclock

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Color
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.util.TimeZone
import com.google.android.material.switchmaterial.SwitchMaterial

class MainActivity : AppCompatActivity(), LocationListener {

    private lateinit var tvCoords: TextView
    private lateinit var tvTime: TextView
    private lateinit var tvDate: TextView
    private lateinit var tvUtc: TextView
    private lateinit var tvHebDate: TextView
    private lateinit var tvHoliday: TextView

    private lateinit var tvGraClock: TextView
    private lateinit var tvMgaClock: TextView
    private lateinit var tvGraMin: TextView
    private lateinit var tvMgaMin: TextView
    private lateinit var tvGraDef: TextView
    private lateinit var tvMgaDef: TextView

    private lateinit var tvSunAlt: TextView
    private lateinit var tvSunAz: TextView
    private lateinit var tvMoonAlt: TextView
    private lateinit var tvMoonAz: TextView
    private lateinit var tvMoonPercent: TextView

    private lateinit var tvZmanimList: TextView

    private lateinit var rgLocation: RadioGroup
    private lateinit var spinnerLocations: Spinner
    private lateinit var rgMga: RadioGroup
    private lateinit var rgSunrise: RadioGroup
    private lateinit var swKeepScreen: SwitchMaterial

    private val handler = Handler(Looper.getMainLooper())
    private lateinit var pythonModule: com.chaquo.python.PyObject
    private var locationManager: LocationManager? = null

    private var currentLat = 31.7768
    private var currentLong = 35.2357
    private var currentAlt = 750.0
    private var currentTimeZoneId = "Asia/Jerusalem"

    private var selectedMgaDeg = -16f
    private var selectedSunDeg = -0.833f

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // --- אתחול TextViews ---
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

        // --- אתחול רכיבי בחירה ---
        rgLocation = findViewById(R.id.rgLocationMode)
        spinnerLocations = findViewById(R.id.spinnerLocations)
        rgMga = findViewById(R.id.rgMga)
        rgSunrise = findViewById(R.id.rgSunrise)
        swKeepScreen = findViewById(R.id.swKeepScreen)

        initPython()
        locationManager = getSystemService(LOCATION_SERVICE) as LocationManager

        // --- בדיקה אם GPS כבוי בתחילת האפליקציה ---
        val prefs = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
        val isGpsSaved = prefs.getBoolean("is_gps", false)
        if (isGpsSaved && !isGpsEnabled()) {
            val toast = Toast.makeText(this, "GPS כבוי, נעבור למיקום מהרשימה", Toast.LENGTH_LONG)
            toast.setGravity(Gravity.TOP or Gravity.CENTER_HORIZONTAL, 0, 200)
            toast.show()
            prefs.edit().putBoolean("is_gps", false).apply()
        }

        setupLocationControls()
        setupMgaSunControls()
        setupKeepScreenControl()
    }

    private fun initPython() {
        if (!Python.isStarted()) Python.start(AndroidPlatform(this))
        pythonModule = Python.getInstance().getModule("logic_api")
    }

    private fun isGpsEnabled(): Boolean {
        return locationManager?.isProviderEnabled(LocationManager.GPS_PROVIDER) ?: false
    }

    private fun setupLocationControls() {
        val locationsJson = pythonModule.callAttr("get_locations_list").toString()
        val locationsList = ArrayList<String>()
        val jsonArray = JSONArray(locationsJson)
        for (i in 0 until jsonArray.length()) locationsList.add(jsonArray.getString(i))

        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, locationsList)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinnerLocations.adapter = adapter

        val prefs = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
        val isGps = prefs.getBoolean("is_gps", false)
        rgLocation.check(if (isGps) R.id.rbGps else R.id.rbList)
        spinnerLocations.isEnabled = !isGps
        spinnerLocations.setSelection(prefs.getInt("location_index", 0))

        rgLocation.setOnCheckedChangeListener { _, id ->
            val usingGps = (id == R.id.rbGps)

            if (usingGps) {
                if (!isGpsEnabled()) {
                    val toast = Toast.makeText(this, "GPS כבוי, נעבור למיקום מהרשימה", Toast.LENGTH_SHORT)
                    toast.setGravity(Gravity.TOP or Gravity.CENTER_HORIZONTAL, 0, 200)
                    toast.show()
                    rgLocation.check(R.id.rbList)
                    spinnerLocations.isEnabled = true
                    updateLocationFromSpinner(spinnerLocations.selectedItemPosition)
                    prefs.edit().putBoolean("is_gps", false).apply()
                } else {
                    spinnerLocations.isEnabled = false
                    prefs.edit().putBoolean("is_gps", true).apply()
                    startGps()
                }
            } else {
                spinnerLocations.isEnabled = true
                updateLocationFromSpinner(spinnerLocations.selectedItemPosition)
                prefs.edit().putBoolean("is_gps", false).apply()
            }

            updateDataImmediate()
        }

        spinnerLocations.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                prefs.edit().putInt("location_index", position).apply()
                if (rgLocation.checkedRadioButtonId == R.id.rbList)
                    updateLocationFromSpinner(position)
                updateDataImmediate()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    private fun setupMgaSunControls() {
        val prefs = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
        selectedMgaDeg = prefs.getFloat("mga_deg", -16f)
        selectedSunDeg = prefs.getFloat("sun_deg", -0.833f)

        rgMga.check(if (selectedMgaDeg == -19.75f) R.id.rbMga19 else R.id.rbMga16)
        rgSunrise.check(if (selectedSunDeg == 0f) R.id.rbSunZero else R.id.rbSunVisible)

        rgMga.setOnCheckedChangeListener { _, checkedId ->
            selectedMgaDeg = if (checkedId == R.id.rbMga19) -19.75f else -16f
            prefs.edit().putFloat("mga_deg", selectedMgaDeg).apply()
            updateDataImmediate()
        }

        rgSunrise.setOnCheckedChangeListener { _, checkedId ->
            selectedSunDeg = if (checkedId == R.id.rbSunZero) 0f else -0.833f
            prefs.edit().putFloat("sun_deg", selectedSunDeg).apply()
            updateDataImmediate()
        }
    }

    private fun setupKeepScreenControl() {
        val prefs = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
        swKeepScreen.isChecked = prefs.getBoolean("keep_screen", true)
        applyKeepScreenSetting()

        swKeepScreen.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("keep_screen", isChecked).apply()
            applyKeepScreenSetting()
        }
    }

    private fun applyKeepScreenSetting() {
        val keepScreen = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
            .getBoolean("keep_screen", true)
        if (keepScreen) window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        else window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }

    override fun onResume() {
        super.onResume()
        startClockLoop()
    }

    override fun onPause() {
        super.onPause()
        handler.removeCallbacksAndMessages(null)
        locationManager?.removeUpdates(this)
    }

    private fun startGps() {
        if (!isGpsEnabled()) {
            val toast = Toast.makeText(this, "GPS כבוי, נעבור למיקום מהרשימה", Toast.LENGTH_SHORT)
            toast.setGravity(Gravity.TOP or Gravity.CENTER_HORIZONTAL, 0, 200)
            toast.show()
            rgLocation.check(R.id.rbList)
            spinnerLocations.isEnabled = true
            updateLocationFromSpinner(spinnerLocations.selectedItemPosition)
            getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
                .edit()
                .putBoolean("is_gps", false)
                .apply()
            updateDataImmediate()
            return
        }

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), 1)
            return
        }

        locationManager?.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000L, 100f, this)
        locationManager?.getLastKnownLocation(LocationManager.GPS_PROVIDER)?.let { onLocationChanged(it) }
    }

    override fun onLocationChanged(loc: Location) {
        currentLat = loc.latitude
        currentLong = loc.longitude
        currentAlt = loc.altitude
        currentTimeZoneId = TimeZone.getDefault().id
    }

    private fun updateLocationFromSpinner(index: Int) {
        val locDataStr = pythonModule.callAttr("get_location_coords", index).toString()
        val locJson = JSONObject(locDataStr)
        currentLat = locJson.getDouble("lat")
        currentLong = locJson.getDouble("long")
        currentAlt = locJson.getDouble("alt")
        currentTimeZoneId = locJson.optString("tz_id", "Asia/Jerusalem")
    }

    private fun startClockLoop() {
        handler.post(object : Runnable {
            override fun run() {
                updateDataImmediate()
                handler.postDelayed(this, 1000)
            }
        })
    }

    private fun updateDataImmediate() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val targetTimeZone = TimeZone.getTimeZone(currentTimeZoneId)
                val offsetMillis = targetTimeZone.getOffset(System.currentTimeMillis())
                val offsetHours = offsetMillis / 3600000.0

                val jsonResultStr = pythonModule.callAttr(
                    "get_data_for_app",
                    currentLat, currentLong, currentAlt,
                    offsetHours, selectedMgaDeg, selectedSunDeg
                ).toString()

                withContext(Dispatchers.Main) { parseAndDisplay(jsonResultStr) }
            } catch (e: Exception) { e.printStackTrace() }
        }
    }

    private fun parseAndDisplay(jsonStr: String) {
        val data = JSONObject(jsonStr)

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
        tvGraMin.text = "${clocks.getString("gra_min")} דקות לשעה"
        tvGraDef.text = clocks.getString("gra_def")

        tvMgaClock.text = clocks.getString("mga_clock")
        tvMgaMin.text = "${clocks.getString("mga_min")} דקות לשעה"
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
        for (i in 0 until timesList.length()) sb.append(timesList.getString(i)).append("\n")
        tvZmanimList.text = sb.toString()
    }
}
