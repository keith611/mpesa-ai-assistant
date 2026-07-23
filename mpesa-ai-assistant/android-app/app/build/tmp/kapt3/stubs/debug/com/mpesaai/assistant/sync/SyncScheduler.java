package com.mpesaai.assistant.sync;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\b\u00c6\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u000e\u0010\u0003\u001a\u00020\u00042\u0006\u0010\u0005\u001a\u00020\u0006\u00a8\u0006\u0007"}, d2 = {"Lcom/mpesaai/assistant/sync/SyncScheduler;", "", "()V", "schedulePeriodicSync", "", "context", "Landroid/content/Context;", "app_debug"})
public final class SyncScheduler {
    @org.jetbrains.annotations.NotNull()
    public static final com.mpesaai.assistant.sync.SyncScheduler INSTANCE = null;
    
    private SyncScheduler() {
        super();
    }
    
    /**
     * Runs every 15 minutes (WorkManager's practical minimum for periodic
     * work) whenever there's connectivity, so any transaction queued while
     * offline eventually syncs even if no new SMS arrives to trigger an
     * immediate sync in the meantime.
     */
    public final void schedulePeriodicSync(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
    }
}