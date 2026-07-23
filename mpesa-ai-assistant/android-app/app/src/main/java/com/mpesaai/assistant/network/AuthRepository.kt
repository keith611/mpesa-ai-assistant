package com.mpesaai.assistant.network

import android.content.Context
import com.mpesaai.assistant.data.PreferencesManager
import com.mpesaai.assistant.network.dto.LoginRequest
import com.mpesaai.assistant.network.dto.RefreshRequest
import com.mpesaai.assistant.network.dto.RegisterRequest

sealed class AuthResult {
    data class Success(val userId: String, val fullName: String) : AuthResult()
    data class Failure(val message: String) : AuthResult()
}

class AuthRepository(private val context: Context) {

    private val prefs = PreferencesManager.getInstance(context)
    private val api get() = RetrofitClient.getInstance(context)

    suspend fun register(fullName: String, phoneNumber: String, whatsappNumber: String, password: String): AuthResult {
        return try {
            val response = api.register(RegisterRequest(fullName, phoneNumber, whatsappNumber, password))
            if (!response.isSuccessful || response.body() == null) {
                return AuthResult.Failure(errorMessage(response.errorBody()?.string(), "Couldn't create your account. The phone number may already be registered."))
            }
            val tokens = response.body()!!
            prefs.accessToken = tokens.access_token
            prefs.refreshToken = tokens.refresh_token

            val profileResponse = api.getProfile("Bearer ${tokens.access_token}")
            if (!profileResponse.isSuccessful || profileResponse.body() == null) {
                return AuthResult.Failure("Account created, but couldn't load your profile. Try signing in.")
            }
            val profile = profileResponse.body()!!
            prefs.linkedUserId = profile.userId
            prefs.linkedUserName = profile.fullName
            AuthResult.Success(profile.userId, profile.fullName)
        } catch (e: Exception) {
            AuthResult.Failure("Couldn't reach the server. Check your connection and the backend URL in Settings.")
        }
    }

    suspend fun login(phoneNumber: String, password: String): AuthResult {
        return try {
            val response = api.login(LoginRequest(phoneNumber, password))
            if (!response.isSuccessful || response.body() == null) {
                return AuthResult.Failure(errorMessage(response.errorBody()?.string(), "Invalid phone number or password."))
            }
            val tokens = response.body()!!
            prefs.accessToken = tokens.access_token
            prefs.refreshToken = tokens.refresh_token

            val profileResponse = api.getProfile("Bearer ${tokens.access_token}")
            if (!profileResponse.isSuccessful || profileResponse.body() == null) {
                return AuthResult.Failure("Signed in, but couldn't load your profile. Try again.")
            }
            val profile = profileResponse.body()!!
            if (profile.role !in listOf("USER", "SUPPORT", "ADMIN", "SUPER_ADMIN")) {
                return AuthResult.Failure("Unrecognized account role.")
            }
            prefs.linkedUserId = profile.userId
            prefs.linkedUserName = profile.fullName
            AuthResult.Success(profile.userId, profile.fullName)
        } catch (e: Exception) {
            AuthResult.Failure("Couldn't reach the server. Check your connection and the backend URL in Settings.")
        }
    }

    /** Attempts to refresh the access token. Returns true on success. */
    suspend fun tryRefresh(): Boolean {
        val refreshToken = prefs.refreshToken ?: return false
        return try {
            val response = api.refresh(RefreshRequest(refreshToken))
            if (response.isSuccessful && response.body() != null) {
                prefs.accessToken = response.body()!!.access_token
                prefs.refreshToken = response.body()!!.refresh_token
                true
            } else {
                false
            }
        } catch (e: Exception) {
            false
        }
    }

    fun logout() {
        prefs.clearAuth()
    }

    private fun errorMessage(body: String?, fallback: String): String {
        if (body.isNullOrBlank()) return fallback
        return try {
            val regex = "\"detail\"\\s*:\\s*\"([^\"]+)\"".toRegex()
            regex.find(body)?.groupValues?.get(1) ?: fallback
        } catch (e: Exception) {
            fallback
        }
    }
}
