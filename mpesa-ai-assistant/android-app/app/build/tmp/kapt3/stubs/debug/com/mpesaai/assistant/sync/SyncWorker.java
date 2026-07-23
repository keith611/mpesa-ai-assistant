package com.mpesaai.assistant.sync;

/**
 * Drains the local pending-transaction queue to the backend's
 * /transactions/ingest endpoint. Runs immediately after a new SMS is
 * parsed (see SmsReceiver) and periodically in the background (see
 * SyncScheduler) so anything that failed while offline eventually goes
 * through once connectivity returns.
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000F\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0003\u0018\u0000 \u00172\u00020\u0001:\u0001\u0017B\u0015\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0002\u0010\u0006J\u000e\u0010\r\u001a\u00020\u000eH\u0096@\u00a2\u0006\u0002\u0010\u000fJ\u001e\u0010\u0010\u001a\u00020\u00112\u0006\u0010\u0012\u001a\u00020\u00132\u0006\u0010\u0014\u001a\u00020\u0015H\u0082@\u00a2\u0006\u0002\u0010\u0016R\u000e\u0010\u0007\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\nX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000b\u001a\u00020\fX\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0018"}, d2 = {"Lcom/mpesaai/assistant/sync/SyncWorker;", "Landroidx/work/CoroutineWorker;", "appContext", "Landroid/content/Context;", "params", "Landroidx/work/WorkerParameters;", "(Landroid/content/Context;Landroidx/work/WorkerParameters;)V", "authRepository", "Lcom/mpesaai/assistant/network/AuthRepository;", "dao", "Lcom/mpesaai/assistant/data/PendingTransactionDao;", "prefs", "Lcom/mpesaai/assistant/data/PreferencesManager;", "doWork", "Landroidx/work/ListenableWorker$Result;", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "trySend", "", "entity", "Lcom/mpesaai/assistant/data/PendingTransactionEntity;", "userId", "", "(Lcom/mpesaai/assistant/data/PendingTransactionEntity;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "Companion", "app_debug"})
public final class SyncWorker extends androidx.work.CoroutineWorker {
    @org.jetbrains.annotations.NotNull()
    private final com.mpesaai.assistant.data.PendingTransactionDao dao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.mpesaai.assistant.data.PreferencesManager prefs = null;
    @org.jetbrains.annotations.NotNull()
    private final com.mpesaai.assistant.network.AuthRepository authRepository = null;
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String IMMEDIATE_WORK_NAME = "mpesa_immediate_sync";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String PERIODIC_WORK_NAME = "mpesa_periodic_sync";
    @org.jetbrains.annotations.NotNull()
    public static final com.mpesaai.assistant.sync.SyncWorker.Companion Companion = null;
    
    public SyncWorker(@org.jetbrains.annotations.NotNull()
    android.content.Context appContext, @org.jetbrains.annotations.NotNull()
    androidx.work.WorkerParameters params) {
        super(null, null);
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.Nullable()
    public java.lang.Object doWork(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super androidx.work.ListenableWorker.Result> $completion) {
        return null;
    }
    
    private final java.lang.Object trySend(com.mpesaai.assistant.data.PendingTransactionEntity entity, java.lang.String userId, kotlin.coroutines.Continuation<? super java.lang.Boolean> $completion) {
        return null;
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\b\u0086\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0006"}, d2 = {"Lcom/mpesaai/assistant/sync/SyncWorker$Companion;", "", "()V", "IMMEDIATE_WORK_NAME", "", "PERIODIC_WORK_NAME", "app_debug"})
    public static final class Companion {
        
        private Companion() {
            super();
        }
    }
}