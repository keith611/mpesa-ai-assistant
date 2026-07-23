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

class RegisterActivity : AppCompatActivity() {

    private lateinit var authRepository: AuthRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)
        authRepository = AuthRepository(this)

        val nameInput = findViewById<TextInputEditText>(R.id.nameInput)
        val phoneInput = findViewById<TextInputEditText>(R.id.phoneInput)
        val whatsappInput = findViewById<TextInputEditText>(R.id.whatsappInput)
        val passwordInput = findViewById<TextInputEditText>(R.id.passwordInput)
        val confirmPasswordInput = findViewById<TextInputEditText>(R.id.confirmPasswordInput)
        val errorText = findViewById<android.widget.TextView>(R.id.errorText)
        val createAccountButton = findViewById<android.widget.Button>(R.id.createAccountButton)
        val loadingIndicator = findViewById<android.widget.ProgressBar>(R.id.loadingIndicator)
        val backToLoginText = findViewById<android.widget.TextView>(R.id.backToLoginText)

        backToLoginText.setOnClickListener {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }

        createAccountButton.setOnClickListener {
            val fullName = nameInput.text?.toString()?.trim().orEmpty()
            val phone = phoneInput.text?.toString()?.trim().orEmpty()
            val whatsappTyped = whatsappInput.text?.toString()?.trim().orEmpty()
            val whatsapp = whatsappTyped.ifEmpty { phone }
            val password = passwordInput.text?.toString().orEmpty()
            val confirmPassword = confirmPasswordInput.text?.toString().orEmpty()

            if (fullName.isEmpty() || phone.isEmpty() || password.isEmpty() || confirmPassword.isEmpty()) {
                showError(errorText, getString(R.string.error_missing_registration_fields))
                return@setOnClickListener
            }
            if (password.length < 8) {
                showError(errorText, getString(R.string.error_password_too_short))
                return@setOnClickListener
            }
            if (password != confirmPassword) {
                showError(errorText, getString(R.string.error_password_mismatch))
                return@setOnClickListener
            }

            errorText.visibility = View.GONE
            loadingIndicator.visibility = View.VISIBLE
            createAccountButton.isEnabled = false

            lifecycleScope.launch {
                val result = authRepository.register(fullName, phone, whatsapp, password)
                loadingIndicator.visibility = View.GONE
                createAccountButton.isEnabled = true

                when (result) {
                    is AuthResult.Success -> requestSmsPermissionsThenContinue()
                    is AuthResult.Failure -> showError(errorText, result.message)
                }
            }
        }
    }

    private fun showError(errorText: android.widget.TextView, message: String) {
        errorText.text = message
        errorText.visibility = View.VISIBLE
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
            goToMain()
        }
    }

    private fun goToMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }

    companion object {
        private const val SMS_PERMISSION_REQUEST_CODE = 1002
    }
}
