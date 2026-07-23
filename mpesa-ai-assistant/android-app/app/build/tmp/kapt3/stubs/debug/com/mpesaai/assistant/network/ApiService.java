package com.mpesaai.assistant.network;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000b\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\bf\u0018\u00002\u00020\u0001J(\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u00062\b\b\u0001\u0010\u0007\u001a\u00020\bH\u00a7@\u00a2\u0006\u0002\u0010\tJ\u001e\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u000b0\u00032\b\b\u0001\u0010\u0007\u001a\u00020\fH\u00a7@\u00a2\u0006\u0002\u0010\rJ\u001e\u0010\u000e\u001a\b\u0012\u0004\u0012\u00020\u000f0\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0010J(\u0010\u0011\u001a\b\u0012\u0004\u0012\u00020\u00040\u00032\b\b\u0001\u0010\u0012\u001a\u00020\u00062\b\b\u0001\u0010\u0007\u001a\u00020\u0013H\u00a7@\u00a2\u0006\u0002\u0010\u0014J\u001e\u0010\u0015\u001a\b\u0012\u0004\u0012\u00020\u00160\u00032\b\b\u0001\u0010\u0007\u001a\u00020\u0017H\u00a7@\u00a2\u0006\u0002\u0010\u0018J\u001e\u0010\u0019\u001a\b\u0012\u0004\u0012\u00020\u00160\u00032\b\b\u0001\u0010\u0007\u001a\u00020\u001aH\u00a7@\u00a2\u0006\u0002\u0010\u001bJ\u001e\u0010\u001c\u001a\b\u0012\u0004\u0012\u00020\u00160\u00032\b\b\u0001\u0010\u0007\u001a\u00020\u001dH\u00a7@\u00a2\u0006\u0002\u0010\u001eJ\u001e\u0010\u001f\u001a\b\u0012\u0004\u0012\u00020\u000b0\u00032\b\b\u0001\u0010\u0007\u001a\u00020 H\u00a7@\u00a2\u0006\u0002\u0010!\u00a8\u0006\""}, d2 = {"Lcom/mpesaai/assistant/network/ApiService;", "", "changePassword", "Lretrofit2/Response;", "", "bearer", "", "request", "Lcom/mpesaai/assistant/network/dto/ChangePasswordRequest;", "(Ljava/lang/String;Lcom/mpesaai/assistant/network/dto/ChangePasswordRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "forgotPassword", "Lcom/mpesaai/assistant/network/dto/MessageResponse;", "Lcom/mpesaai/assistant/network/dto/ForgotPasswordRequest;", "(Lcom/mpesaai/assistant/network/dto/ForgotPasswordRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getProfile", "Lcom/mpesaai/assistant/network/dto/UserProfileResponse;", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "ingestTransaction", "deviceApiKey", "Lcom/mpesaai/assistant/network/dto/TransactionIngestRequest;", "(Ljava/lang/String;Lcom/mpesaai/assistant/network/dto/TransactionIngestRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "login", "Lcom/mpesaai/assistant/network/dto/TokenResponse;", "Lcom/mpesaai/assistant/network/dto/LoginRequest;", "(Lcom/mpesaai/assistant/network/dto/LoginRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "refresh", "Lcom/mpesaai/assistant/network/dto/RefreshRequest;", "(Lcom/mpesaai/assistant/network/dto/RefreshRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "register", "Lcom/mpesaai/assistant/network/dto/RegisterRequest;", "(Lcom/mpesaai/assistant/network/dto/RegisterRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "resetPassword", "Lcom/mpesaai/assistant/network/dto/ResetPasswordRequest;", "(Lcom/mpesaai/assistant/network/dto/ResetPasswordRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public abstract interface ApiService {
    
    @retrofit2.http.POST(value = "auth/register")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object register(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.mpesaai.assistant.network.dto.RegisterRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.mpesaai.assistant.network.dto.TokenResponse>> $completion);
    
    @retrofit2.http.POST(value = "auth/login")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object login(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.mpesaai.assistant.network.dto.LoginRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.mpesaai.assistant.network.dto.TokenResponse>> $completion);
    
    @retrofit2.http.POST(value = "auth/forgot-password")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object forgotPassword(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.mpesaai.assistant.network.dto.ForgotPasswordRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.mpesaai.assistant.network.dto.MessageResponse>> $completion);
    
    @retrofit2.http.POST(value = "auth/reset-password")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object resetPassword(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.mpesaai.assistant.network.dto.ResetPasswordRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.mpesaai.assistant.network.dto.MessageResponse>> $completion);
    
    @retrofit2.http.POST(value = "auth/change-password")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object changePassword(@retrofit2.http.Header(value = "Authorization")
    @org.jetbrains.annotations.NotNull()
    java.lang.String bearer, @retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.mpesaai.assistant.network.dto.ChangePasswordRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<kotlin.Unit>> $completion);
    
    @retrofit2.http.POST(value = "auth/refresh")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object refresh(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.mpesaai.assistant.network.dto.RefreshRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.mpesaai.assistant.network.dto.TokenResponse>> $completion);
    
    @retrofit2.http.GET(value = "users/me")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getProfile(@retrofit2.http.Header(value = "Authorization")
    @org.jetbrains.annotations.NotNull()
    java.lang.String bearer, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.mpesaai.assistant.network.dto.UserProfileResponse>> $completion);
    
    @retrofit2.http.POST(value = "transactions/ingest")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object ingestTransaction(@retrofit2.http.Header(value = "X-Device-Api-Key")
    @org.jetbrains.annotations.NotNull()
    java.lang.String deviceApiKey, @retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.mpesaai.assistant.network.dto.TransactionIngestRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<kotlin.Unit>> $completion);
}