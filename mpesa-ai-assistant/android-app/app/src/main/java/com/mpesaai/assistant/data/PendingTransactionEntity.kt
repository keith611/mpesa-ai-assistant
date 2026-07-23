package com.mpesaai.assistant.data

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * A parsed M-Pesa transaction waiting to be synced to the backend.
 * Rows are removed once successfully ingested (or once the backend
 * confirms it's a duplicate — see SyncWorker).
 *
 * transactionCode has a unique index so if the SmsReceiver ever fires
 * twice for the same message (rare but possible on some devices), the
 * second insert is silently ignored rather than creating a duplicate
 * queue entry.
 */
@Entity(
    tableName = "pending_transactions",
    indices = [Index(value = ["transactionCode"], unique = true)]
)
data class PendingTransactionEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val transactionCode: String,
    val amount: Double,
    val transactionType: String,
    val sender: String,
    val receiver: String,
    val paybillNumber: String,
    val tillNumber: String,
    val accountReference: String,
    val date: String,
    val time: String,
    val balance: Double?,
    val rawSmsBody: String,
    val receivedAtMillis: Long,
    val syncAttempts: Int = 0,
    val lastError: String? = null,
)
