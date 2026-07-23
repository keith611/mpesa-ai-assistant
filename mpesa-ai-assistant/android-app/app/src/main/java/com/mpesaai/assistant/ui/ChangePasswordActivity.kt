package com.mpesaai.assistant.ui

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import com.mpesaai.assistant.R
import com.mpesaai.assistant.network.RetrofitClient
import com.mpesaai.assistant.network.dto.ChangePasswordRequest
import com.mpesaai.assistant.data.PreferencesManager
import kotlinx.coroutines.launch

/**
 * Lets a signed-in user change their password directly, without going
 * through the WhatsApp reset-code flow. Requires the current password.
 */
class ChangePasswordActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_change_password)

        val currentPasswordInput = findViewById<TextInputEditText>(R.id.currentPasswordInput)
        val newPasswordInput = findViewById<TextInputEditText>(R.id.newPasswordInput)
        val statusText = findViewById<android.widget.TextView>(R.id.statusText)
        val changePasswordButton = findViewById<android.widget.Button>(R.id.changePasswordButton)
        val loadingIndicator = findViewById<android.widget.ProgressBar>(R.id.loadingIndicator)

        val api = RetrofitClient.getInstance(this)
        val prefs = PreferencesManager.getInstance(this)

        changePasswordButton.setOnClickListener {
            val currentPassword = currentPasswordInput.text?.toString().orEmpty()
            val newPassword = newPasswordInput.text?.toString().orEmpty()

            if (currentPassword.isEmpty() || newPassword.isEmpty()) {
                showStatus(statusText, "Enter both your current and new password.", isError = true)
                return@setOnClickListener
            }
            if (newPassword.length < 8) {
                showStatus(statusText, "New password must be at least 8 characters.", isError = true)
                return@setOnClickListener
            }

            loadingIndicator.visibility = View.VISIBLE
            changePasswordButton.isEnabled = false

            lifecycleScope.launch {
                try {
                    val token = prefs.accessToken
                    val response = api.changePassword(
                        "Bearer $token",
                        ChangePasswordRequest(currentPassword, newPassword)
                    )
                    if (response.isSuccessful) {
                        showStatus(statusText, "Password changed successfully.", isError = false)
                        currentPasswordInput.text?.clear()
                        newPasswordInput.text?.clear()
                    } else if (response.code() == 400) {
                        showStatus(statusText, "Current password is incorrect.", isError = true)
                    } else {
                        showStatus(statusText, "Couldn't change password. Try again.", isError = true)
                    }
                } catch (e: Exception) {
                    showStatus(statusText, "Couldn't reach the server. Check your connection.", isError = true)
                } finally {
                    loadingIndicator.visibility = View.GONE
                    changePasswordButton.isEnabled = true
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
