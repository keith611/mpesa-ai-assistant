package com.mpesaai.assistant.network;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\"\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0000\b\u00c6\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u0010\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0006\u001a\u00020\u0007H\u0002J\u000e\u0010\b\u001a\u00020\u00042\u0006\u0010\u0006\u001a\u00020\u0007J\u0006\u0010\t\u001a\u00020\nR\u0010\u0010\u0003\u001a\u0004\u0018\u00010\u0004X\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u000b"}, d2 = {"Lcom/mpesaai/assistant/network/RetrofitClient;", "", "()V", "apiService", "Lcom/mpesaai/assistant/network/ApiService;", "build", "context", "Landroid/content/Context;", "getInstance", "reset", "", "app_debug"})
public final class RetrofitClient {
    @kotlin.jvm.Volatile()
    @org.jetbrains.annotations.Nullable()
    private static volatile com.mpesaai.assistant.network.ApiService apiService;
    @org.jetbrains.annotations.NotNull()
    public static final com.mpesaai.assistant.network.RetrofitClient INSTANCE = null;
    
    private RetrofitClient() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.mpesaai.assistant.network.ApiService getInstance(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        return null;
    }
    
    private final com.mpesaai.assistant.network.ApiService build(android.content.Context context) {
        return null;
    }
    
    /**
     * Call after the base URL setting changes so the next request uses it.
     */
    public final void reset() {
    }
}