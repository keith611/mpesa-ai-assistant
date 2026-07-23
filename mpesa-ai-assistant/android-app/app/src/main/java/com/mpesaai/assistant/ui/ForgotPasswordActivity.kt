package com.mpesaai.assistant.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import com.mpesaai.assistant.R
import com.mpesaai.assistant.network.RetrofitClient
import com.mpesaai.assistant.network.dto.ForgotPasswordRequest
import com.mpesaai.assistant.network.dto.ResetPasswordRequest
import kotlinx.coroutines.launch

class ForgotPasswordActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_forgot_password)

        val phoneInput = findViewById<TextInputEditText>(R.id.phoneInput)
        val requestCodeButton = findViewById<android.widget.Button>(R.id.requestCodeButton)
        val codeLayout = findViewById<View>(R.id.codeLayout)
        val codeInput = findViewById<TextInputEditText>(R.id.codeInput)
        val newPasswordLayout = findViewById<View>(R.id.newPasswordLayout)
        val newPasswordInput = findViewById<TextInputEditText>(R.id.newPasswordInput)
        val confirmResetButton = findViewById<android.widget.Button>(R.id.confirmResetButton)
        val statusText = findViewById<android.widget.TextView>(R.id.statusText)
        val loadingIndicator = findViewById<android.widget.ProgressBar>(R.id.loadingIndicator)
        val backToLoginText = findViewById<android.widget.TextView>(R.id.backToLoginText)

        val api = RetrofitClient.getInstance(this)

        backToLoginText.setOnClickListener {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }

        requestCodeButton.setOnClickListener {
            val phone = phoneInput.text?.toString()?.trim().orEmpty()
            if (phone.isEmpty()) {
                showStatus(statusText, "Enter your phone number first.", isError = true)
                return@setOnClickListener
            }

            loadingIndicator.visibility = View.VISIBLE
            requestCodeButton.isEnabled = false

            lifecycleScope.launch {
                try {
                    api.forgotPassword(ForgotPasswordRequest(phone))
                    showStatus(statusText, getString(R.string.reset_code_sent), isError = false)
                    codeLayout.visibility = View.VISIBLE
                    newPasswordLayout.visibility = View.VISIBLE
                    confirmResetButton.visibility = View.VISIBLE
                } catch (e: Exception) {
                    showStatus(statusText, "Couldn't reach the server. Check your connection.", isError = true)
                } finally {
                    loadingIndicator.visibility = View.GONE
                    requestCodeButton.isEnabled = true
                }
            }
        }

        confirmResetButton.setOnClickListener {
            val phone = phoneInput.text?.toString()?.trim().orEmpty()
            val code = codeInput.text?.toString()?.trim().orEmpty()
            val newPassword = newPasswordInput.text?.toString().orEmpty()

            if (code.isEmpty() || newPassword.isEmpty()) {
                showStatus(statusText, "Enter the code and your new password.", isError = true)
                return@setOnClickListener
            }
            if (newPassword.length < 8) {
                showStatus(statusText, getString(R.string.error_password_too_short), isError = true)
                return@setOnClickListener
            }

            loadingIndicator.visibility = View.VISIBLE
            confirmResetButton.isEnabled = false

            lifecycleScope.launch {
                try {
                    val response = api.resetPassword(ResetPasswordRequest(phone, code, newPassword))
                    if (response.isSuccessful) {
                        showStatus(statusText, getString(R.string.reset_success), isError = false)
                        codeInput.text?.clear()
                        newPasswordInput.text?.clear()
                    } else {
                        showStatus(statusText, "Incorrect or expired code. Request a new one.", isError = true)
                    }
                } catch (e: Exception) {
                    showStatus(statusText, "Couldn't reach the server. Check your connection.", isError = true)
                } finally {
                    loadingIndicator.visibility = View.GONE
                    confirmResetButton.isEnabled = true
                }
            }
        }
    }

    private fun showStatus(view: android.widget.TextView, message: String, isError: Boolean) {
        view.text = message
        view.setTextColor(getColor(if (isError) R.color.danger else R.color.success))
        view.visibility = View.VISIBLE
    }
}
