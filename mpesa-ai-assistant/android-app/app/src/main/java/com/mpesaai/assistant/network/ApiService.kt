package com.mpesaai.assistant.network

import com.mpesaai.assistant.network.dto.ForgotPasswordRequest
import com.mpesaai.assistant.network.dto.ChangePasswordRequest
import com.mpesaai.assistant.network.dto.LoginRequest
import com.mpesaai.assistant.network.dto.MessageResponse
import com.mpesaai.assistant.network.dto.RefreshRequest
import com.mpesaai.assistant.network.dto.RegisterRequest
import com.mpesaai.assistant.network.dto.ResetPasswordRequest
import com.mpesaai.assistant.network.dto.TokenResponse
import com.mpesaai.assistant.network.dto.TransactionIngestRequest
import com.mpesaai.assistant.network.dto.UserProfileResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST

interface ApiService {

    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<TokenResponse>

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<TokenResponse>

    @POST("auth/forgot-password")
    suspend fun forgotPassword(@Body request: ForgotPasswordRequest): Response<MessageResponse>

    @POST("auth/reset-password")
    suspend fun resetPassword(@Body request: ResetPasswordRequest): Response<MessageResponse>
@POST("auth/change-password")
suspend fun changePassword(
    @Header("Authorization") bearer: String,
    @Body request: ChangePasswordRequest
): Response<Unit>

    @POST("auth/refresh")
    suspend fun refresh(@Body request: RefreshRequest): Response<TokenResponse>

    @GET("users/me")
    suspend fun getProfile(@Header("Authorization") bearer: String): Response<UserProfileResponse>

    // Protected by the shared device API key, NOT by the user's JWT — this is
    // what lets the app keep ingesting transactions even if the JWT expires
    // between syncs (the device key never expires and is rotated manually).
    @POST("transactions/ingest")
    suspend fun ingestTransaction(
        @Header("X-Device-Api-Key") deviceApiKey: String,
        @Body request: TransactionIngestRequest
    ): Response<Unit>
}
