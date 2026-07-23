package com.mpesaai.assistant.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.mpesaai.assistant.data.PreferencesManager

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = PreferencesManager.getInstance(this)
        val next = if (prefs.isLoggedIn()) MainActivity::class.java else LoginActivity::class.java
        startActivity(Intent(this, next))
        finish()
    }
}
