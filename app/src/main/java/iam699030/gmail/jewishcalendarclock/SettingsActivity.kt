package iam699030.gmail.jewishcalendarclock

import android.content.Context
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import org.json.JSONArray
import com.google.android.material.switchmaterial.SwitchMaterial


class SettingsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        val prefs = getSharedPreferences("HalachaPrefs", Context.MODE_PRIVATE)
        val editor = prefs.edit()

        // רכיבים
        val rgLocation = findViewById<RadioGroup>(R.id.rgLocationMode)
        val spinner = findViewById<Spinner>(R.id.spinnerLocations)
        val rgMga = findViewById<RadioGroup>(R.id.rgMga)
        val rgSunrise = findViewById<RadioGroup>(R.id.rgSunrise)
        val swKeepScreen: SwitchMaterial = findViewById(R.id.swKeepScreen)
        val btnSave = findViewById<Button>(R.id.btnSave)

        // טעינת רשימת המיקומים מפייתון
        val py = Python.getInstance()
        val logic = py.getModule("logic_api")
        val locationsJson = logic.callAttr("get_locations_list").toString()
        val locationsList = ArrayList<String>()
        val jsonArray = JSONArray(locationsJson)
        for (i in 0 until jsonArray.length()) {
            locationsList.add(jsonArray.getString(i))
        }

        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, locationsList)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinner.adapter = adapter

        // טעינת מצב קיים
        val isGps = prefs.getBoolean("is_gps", false)
        rgLocation.check(if (isGps) R.id.rbGps else R.id.rbList)
        spinner.isEnabled = !isGps
        spinner.setSelection(prefs.getInt("location_index", 0))

        val mgaDeg = prefs.getFloat("mga_deg", -16f)
        rgMga.check(if (mgaDeg == -19.75f) R.id.rbMga19 else R.id.rbMga16)

        val sunDeg = prefs.getFloat("sun_deg", -0.833f)
        rgSunrise.check(if (sunDeg == 0f) R.id.rbSunZero else R.id.rbSunVisible)

        swKeepScreen.isChecked = prefs.getBoolean("keep_screen", true)

        // לוגיקה
        rgLocation.setOnCheckedChangeListener { _, id ->
            spinner.isEnabled = (id == R.id.rbList)
        }

        btnSave.setOnClickListener {
            editor.putBoolean("is_gps", rgLocation.checkedRadioButtonId == R.id.rbGps)
            editor.putInt("location_index", spinner.selectedItemPosition)

            val selectedMga = if (rgMga.checkedRadioButtonId == R.id.rbMga19) -19.75f else -16f
            editor.putFloat("mga_deg", selectedMga)

            val selectedSun = if (rgSunrise.checkedRadioButtonId == R.id.rbSunZero) 0f else -0.833f
            editor.putFloat("sun_deg", selectedSun)

            editor.putBoolean("keep_screen", swKeepScreen.isChecked)

            editor.apply()
            finish() // חזרה למסך הראשי
        }
    }
}