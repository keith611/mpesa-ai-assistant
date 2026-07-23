package com.mpesaai.assistant.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import com.mpesaai.assistant.R
import com.mpesaai.assistant.network.AuthRepository
import com.mpesaai.assistant.network.AuthResult
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    private lateinit var authRepository: AuthRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        authRepository = AuthRepository(this)

        val phoneInput = findViewById<TextInputEditText>(R.id.phoneInput)
        val passwordInput = findViewById<TextInputEditText>(R.id.passwordInput)
        val errorText = findViewById<android.widget.TextView>(R.id.errorText)
        val signInButton = findViewById<android.widget.Button>(R.id.signInButton)
        val loadingIndicator = findViewById<android.widget.ProgressBar>(R.id.loadingIndicator)
        val goToRegisterText = findViewById<android.widget.TextView>(R.id.goToRegisterText)
        val forgotPasswordText = findViewById<android.widget.TextView>(R.id.forgotPasswordText)

        goToRegisterText.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        forgotPasswordText.setOnClickListener {
            startActivity(Intent(this, ForgotPasswordActivity::class.java))
        }

        signInButton.setOnClickListener {
            val phone = phoneInput.text?.toString()?.trim().orEmpty()
            val password = passwordInput.text?.toString().orEmpty()

            if (phone.isEmpty() || password.isEmpty()) {
                errorText.text = getString(R.string.error_missing_fields)
                errorText.visibility = View.VISIBLE
                return@setOnClickListener
            }

            errorText.visibility = View.GONE
            loadingIndicator.visibility = View.VISIBLE
            signInButton.isEnabled = false

            lifecycleScope.launch {
                val result = authRepository.login(phone, password)
                loadingIndicator.visibility = View.GONE
                signInButton.isEnabled = true

                when (result) {
                    is AuthResult.Success -> requestSmsPermissionsThenContinue()
                    is AuthResult.Failure -> {
                        errorText.text = result.message
                        errorText.visibility = View.VISIBLE
                    }
                }
            }
        }
    }

    private fun requestSmsPermissionsThenContinue() {
        val permissions = arrayOf(Manifest.permission.RECEIVE_SMS, Manifest.permission.READ_SMS)
        val allGranted = permissions.all {
            ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
        }
        if (allGranted) {
            goToMain()
        } else {
            ActivityCompat.requestPermissions(this, permissions, SMS_PERMISSION_REQUEST_CODE)
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == SMS_PERMISSION_REQUEST_CODE) {
            // Proceed regardless — MainActivity shows a clear banner if permissions
            // are still missing, and lets the user retry from Settings.
            goToMain()
        }
    }

    private fun goToMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }

    companion object {
        private const val SMS_PERMISSION_REQUEST_CODE = 1001
    }
}
