package com.mpesaai.assistant.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequest
import androidx.work.WorkManager
import com.mpesaai.assistant.data.AppDatabase
import com.mpesaai.assistant.data.PendingTransactionEntity
import com.mpesaai.assistant.sync.SyncWorker
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Listens for incoming SMS. We never call abortBroadcast() — the user's
 * default Messages app still receives and displays every SMS normally.
 * We only additionally parse M-Pesa alerts and queue them for sync.
 */
class SmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        val appContext = context.applicationContext

        for (message in messages) {
            val sender = message.originatingAddress
            val body = message.messageBody ?: continue

            if (!MpesaSmsParser.isMpesaSender(sender)) continue

            val parsed = MpesaSmsParser.parse(body)
            if (parsed == null) {
                Log.w(TAG, "Received M-Pesa SMS but couldn't parse it: ${body.take(40)}...")
                continue
            }

            // Persist immediately on a background coroutine, then trigger a sync attempt.
            // Using a plain CoroutineScope here (not viewModelScope) since a
            // BroadcastReceiver has no lifecycle of its own.
            CoroutineScope(Dispatchers.IO).launch {
                val dao = AppDatabase.getInstance(appContext).pendingTransactionDao()
                val alreadyQueued = dao.existsByCode(parsed.transactionCode)
                if (!alreadyQueued) {
                    dao.insert(
                        PendingTransactionEntity(
                            transactionCode = parsed.transactionCode,
                            amount = parsed.amount,
                            transactionType = parsed.transactionType,
                            sender = parsed.sender,
                            receiver = parsed.receiver,
                            paybillNumber = parsed.paybillNumber,
                            tillNumber = parsed.tillNumber,
                            accountReference = parsed.accountReference,
                            date = parsed.date,
                            time = parsed.time,
                            balance = parsed.balance,
                            rawSmsBody = body,
                            receivedAtMillis = System.currentTimeMillis(),
                        )
                    )
                }
                enqueueSync(appContext)
            }
        }
    }

    private fun enqueueSync(context: Context) {
        val request = OneTimeWorkRequest.Builder(SyncWorker::class.java).build()
        WorkManager.getInstance(context).enqueueUniqueWork(
            SyncWorker.IMMEDIATE_WORK_NAME,
            ExistingWorkPolicy.KEEP,
            request
        )
    }

    companion object {
        private const val TAG = "SmsReceiver"
    }
}
