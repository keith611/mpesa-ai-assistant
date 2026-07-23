package com.mpesaai.assistant.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update

@Dao
interface PendingTransactionDao {

    // Transaction codes are unique per M-Pesa message; IGNORE means a
    // duplicate SMS (e.g. the receiver firing twice) is silently dropped
    // at the device level, before it ever reaches the backend.
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(entity: PendingTransactionEntity): Long

    @Update
    suspend fun update(entity: PendingTransactionEntity)

    @Query("SELECT * FROM pending_transactions ORDER BY receivedAtMillis ASC")
    suspend fun getAllPending(): List<PendingTransactionEntity>

    @Query("SELECT COUNT(*) FROM pending_transactions")
    suspend fun countPending(): Int

    @Query("SELECT EXISTS(SELECT 1 FROM pending_transactions WHERE transactionCode = :code)")
    suspend fun existsByCode(code: String): Boolean

    @Query("DELETE FROM pending_transactions WHERE id = :id")
    suspend fun deleteById(id: Long)

    @Query("SELECT * FROM pending_transactions ORDER BY receivedAtMillis DESC LIMIT :limit")
    suspend fun getRecent(limit: Int): List<PendingTransactionEntity>
}
