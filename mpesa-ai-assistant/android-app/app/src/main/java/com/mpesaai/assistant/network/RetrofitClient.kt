package com.mpesaai.assistant.network

import android.content.Context
import com.mpesaai.assistant.BuildConfig
import com.mpesaai.assistant.data.PreferencesManager
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    @Volatile private var apiService: ApiService? = null

    fun getInstance(context: Context): ApiService =
        apiService ?: synchronized(this) {
            apiService ?: build(context).also { apiService = it }
        }

    private fun build(context: Context): ApiService {
        val prefs = PreferencesManager.getInstance(context)

        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)
            .build()

        return Retrofit.Builder()
            .baseUrl(prefs.apiBaseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }

    /** Call after the base URL setting changes so the next request uses it. */
    fun reset() {
        apiService = null
    }
}
