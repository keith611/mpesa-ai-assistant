package com.mpesaai.assistant.network.dto

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val phone_number: String,
    val password: String
)

data class RegisterRequest(
    val full_name: String,
    val phone_number: String,
    val whatsapp_number: String,
    val password: String
)

data class ForgotPasswordRequest(
    val phone_number: String
)

data class ResetPasswordRequest(
    val phone_number: String,
    val code: String,
    val new_password: String
)

data class MessageResponse(
    val message: String
)

data class TokenResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String
)

data class RefreshRequest(
    val refresh_token: String
)

data class UserProfileResponse(
    @SerializedName("User ID") val userId: String,
    @SerializedName("Full Name") val fullName: String,
    @SerializedName("Phone Number") val phoneNumber: String,
    @SerializedName("WhatsApp Number") val whatsappNumber: String,
    @SerializedName("Role") val role: String,
    @SerializedName("Status") val status: String
)

data class TransactionIngestRequest(
    val user_id: String,
    val transaction_code: String,
    val amount: Double,
    val transaction_type: String,
    val sender: String = "",
    val receiver: String = "",
    val paybill_number: String = "",
    val till_number: String = "",
    val account_reference: String = "",
    val date: String = "",
    val time: String = "",
    val balance: Double? = null
)

data class ChangePasswordRequest(
    val current_password: String,
    val new_password: String
)
