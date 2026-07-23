package com.mpesaai.assistant.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.mpesaai.assistant.BuildConfig
import com.mpesaai.assistant.data.AppDatabase
import com.mpesaai.assistant.data.PendingTransactionEntity
import com.mpesaai.assistant.data.PreferencesManager
import com.mpesaai.assistant.network.AuthRepository
import com.mpesaai.assistant.network.RetrofitClient
import com.mpesaai.assistant.network.dto.TransactionIngestRequest

/**
 * Drains the local pending-transaction queue to the backend's
 * /transactions/ingest endpoint. Runs immediately after a new SMS is
 * parsed (see SmsReceiver) and periodically in the background (see
 * SyncScheduler) so anything that failed while offline eventually goes
 * through once connectivity returns.
 */
class SyncWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {

    private val dao = AppDatabase.getInstance(appContext).pendingTransactionDao()
    private val prefs = PreferencesManager.getInstance(appContext)
    private val authRepository = AuthRepository(appContext)

    override suspend fun doWork(): Result {
        if (!prefs.isLoggedIn()) {
            // Nothing to sync to — the device hasn't been linked to an account yet.
            return Result.success()
        }

        val userId = prefs.linkedUserId ?: return Result.success()
        val pending = dao.getAllPending()
        if (pending.isEmpty()) return Result.success()

        var anyFailure = false

        for (entity in pending) {
            val success = trySend(entity, userId)
            if (success) {
                dao.deleteById(entity.id)
            } else {
                anyFailure = true
                dao.update(entity.copy(syncAttempts = entity.syncAttempts + 1))
            }
        }

        // Let WorkManager retry later (with backoff, configured in SyncScheduler)
        // if anything failed for a reason other than "already exists".
        return if (anyFailure) Result.retry() else Result.success()
    }

    private suspend fun trySend(entity: PendingTransactionEntity, userId: String): Boolean {
        val api = RetrofitClient.getInstance(applicationContext)
        val request = TransactionIngestRequest(
            user_id = userId,
            transaction_code = entity.transactionCode,
            amount = entity.amount,
            transaction_type = entity.transactionType,
            sender = entity.sender,
            receiver = entity.receiver,
            paybill_number = entity.paybillNumber,
            till_number = entity.tillNumber,
            account_reference = entity.accountReference,
            date = entity.date,
            time = entity.time,
            balance = entity.balance,
        )

        return try {
            val response = api.ingestTransaction(BuildConfig.DEVICE_API_KEY, request)
            when {
                response.isSuccessful -> true
                // 409 = backend already has this transaction code recorded.
                // Treat as success from the device's point of view — remove
                // it from the local queue rather than retrying forever.
                response.code() == 409 -> true
                else -> false
            }
        } catch (e: Exception) {
            false
        }
    }

    companion object {
        const val IMMEDIATE_WORK_NAME = "mpesa_immediate_sync"
        const val PERIODIC_WORK_NAME = "mpesa_periodic_sync"
    }
}
