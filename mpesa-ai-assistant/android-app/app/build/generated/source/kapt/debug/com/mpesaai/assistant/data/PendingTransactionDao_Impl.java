package com.mpesaai.assistant.data;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityDeletionOrUpdateAdapter;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import java.lang.Boolean;
import java.lang.Class;
import java.lang.Double;
import java.lang.Exception;
import java.lang.Integer;
import java.lang.Long;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class PendingTransactionDao_Impl implements PendingTransactionDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<PendingTransactionEntity> __insertionAdapterOfPendingTransactionEntity;

  private final EntityDeletionOrUpdateAdapter<PendingTransactionEntity> __updateAdapterOfPendingTransactionEntity;

  private final SharedSQLiteStatement __preparedStmtOfDeleteById;

  public PendingTransactionDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfPendingTransactionEntity = new EntityInsertionAdapter<PendingTransactionEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR IGNORE INTO `pending_transactions` (`id`,`transactionCode`,`amount`,`transactionType`,`sender`,`receiver`,`paybillNumber`,`tillNumber`,`accountReference`,`date`,`time`,`balance`,`rawSmsBody`,`receivedAtMillis`,`syncAttempts`,`lastError`) VALUES (nullif(?, 0),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final PendingTransactionEntity entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getTransactionCode() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getTransactionCode());
        }
        statement.bindDouble(3, entity.getAmount());
        if (entity.getTransactionType() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getTransactionType());
        }
        if (entity.getSender() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getSender());
        }
        if (entity.getReceiver() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getReceiver());
        }
        if (entity.getPaybillNumber() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getPaybillNumber());
        }
        if (entity.getTillNumber() == null) {
          statement.bindNull(8);
        } else {
          statement.bindString(8, entity.getTillNumber());
        }
        if (entity.getAccountReference() == null) {
          statement.bindNull(9);
        } else {
          statement.bindString(9, entity.getAccountReference());
        }
        if (entity.getDate() == null) {
          statement.bindNull(10);
        } else {
          statement.bindString(10, entity.getDate());
        }
        if (entity.getTime() == null) {
          statement.bindNull(11);
        } else {
          statement.bindString(11, entity.getTime());
        }
        if (entity.getBalance() == null) {
          statement.bindNull(12);
        } else {
          statement.bindDouble(12, entity.getBalance());
        }
        if (entity.getRawSmsBody() == null) {
          statement.bindNull(13);
        } else {
          statement.bindString(13, entity.getRawSmsBody());
        }
        statement.bindLong(14, entity.getReceivedAtMillis());
        statement.bindLong(15, entity.getSyncAttempts());
        if (entity.getLastError() == null) {
          statement.bindNull(16);
        } else {
          statement.bindString(16, entity.getLastError());
        }
      }
    };
    this.__updateAdapterOfPendingTransactionEntity = new EntityDeletionOrUpdateAdapter<PendingTransactionEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `pending_transactions` SET `id` = ?,`transactionCode` = ?,`amount` = ?,`transactionType` = ?,`sender` = ?,`receiver` = ?,`paybillNumber` = ?,`tillNumber` = ?,`accountReference` = ?,`date` = ?,`time` = ?,`balance` = ?,`rawSmsBody` = ?,`receivedAtMillis` = ?,`syncAttempts` = ?,`lastError` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final PendingTransactionEntity entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getTransactionCode() == null) {
          statement.bindNull(2);
        } else {
          statement.bindString(2, entity.getTransactionCode());
        }
        statement.bindDouble(3, entity.getAmount());
        if (entity.getTransactionType() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getTransactionType());
        }
        if (entity.getSender() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getSender());
        }
        if (entity.getReceiver() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getReceiver());
        }
        if (entity.getPaybillNumber() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getPaybillNumber());
        }
        if (entity.getTillNumber() == null) {
          statement.bindNull(8);
        } else {
          statement.bindString(8, entity.getTillNumber());
        }
        if (entity.getAccountReference() == null) {
          statement.bindNull(9);
        } else {
          statement.bindString(9, entity.getAccountReference());
        }
        if (entity.getDate() == null) {
          statement.bindNull(10);
        } else {
          statement.bindString(10, entity.getDate());
        }
        if (entity.getTime() == null) {
          statement.bindNull(11);
        } else {
          statement.bindString(11, entity.getTime());
        }
        if (entity.getBalance() == null) {
          statement.bindNull(12);
        } else {
          statement.bindDouble(12, entity.getBalance());
        }
        if (entity.getRawSmsBody() == null) {
          statement.bindNull(13);
        } else {
          statement.bindString(13, entity.getRawSmsBody());
        }
        statement.bindLong(14, entity.getReceivedAtMillis());
        statement.bindLong(15, entity.getSyncAttempts());
        if (entity.getLastError() == null) {
          statement.bindNull(16);
        } else {
          statement.bindString(16, entity.getLastError());
        }
        statement.bindLong(17, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteById = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM pending_transactions WHERE id = ?";
        return _query;
      }
    };
  }

  @Override
  public Object insert(final PendingTransactionEntity entity,
      final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfPendingTransactionEntity.insertAndReturnId(entity);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object update(final PendingTransactionEntity entity,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfPendingTransactionEntity.handle(entity);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteById(final long id, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteById.acquire();
        int _argIndex = 1;
        _stmt.bindLong(_argIndex, id);
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfDeleteById.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Object getAllPending(
      final Continuation<? super List<PendingTransactionEntity>> $completion) {
    final String _sql = "SELECT * FROM pending_transactions ORDER BY receivedAtMillis ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<PendingTransactionEntity>>() {
      @Override
      @NonNull
      public List<PendingTransactionEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfTransactionCode = CursorUtil.getColumnIndexOrThrow(_cursor, "transactionCode");
          final int _cursorIndexOfAmount = CursorUtil.getColumnIndexOrThrow(_cursor, "amount");
          final int _cursorIndexOfTransactionType = CursorUtil.getColumnIndexOrThrow(_cursor, "transactionType");
          final int _cursorIndexOfSender = CursorUtil.getColumnIndexOrThrow(_cursor, "sender");
          final int _cursorIndexOfReceiver = CursorUtil.getColumnIndexOrThrow(_cursor, "receiver");
          final int _cursorIndexOfPaybillNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "paybillNumber");
          final int _cursorIndexOfTillNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "tillNumber");
          final int _cursorIndexOfAccountReference = CursorUtil.getColumnIndexOrThrow(_cursor, "accountReference");
          final int _cursorIndexOfDate = CursorUtil.getColumnIndexOrThrow(_cursor, "date");
          final int _cursorIndexOfTime = CursorUtil.getColumnIndexOrThrow(_cursor, "time");
          final int _cursorIndexOfBalance = CursorUtil.getColumnIndexOrThrow(_cursor, "balance");
          final int _cursorIndexOfRawSmsBody = CursorUtil.getColumnIndexOrThrow(_cursor, "rawSmsBody");
          final int _cursorIndexOfReceivedAtMillis = CursorUtil.getColumnIndexOrThrow(_cursor, "receivedAtMillis");
          final int _cursorIndexOfSyncAttempts = CursorUtil.getColumnIndexOrThrow(_cursor, "syncAttempts");
          final int _cursorIndexOfLastError = CursorUtil.getColumnIndexOrThrow(_cursor, "lastError");
          final List<PendingTransactionEntity> _result = new ArrayList<PendingTransactionEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final PendingTransactionEntity _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpTransactionCode;
            if (_cursor.isNull(_cursorIndexOfTransactionCode)) {
              _tmpTransactionCode = null;
            } else {
              _tmpTransactionCode = _cursor.getString(_cursorIndexOfTransactionCode);
            }
            final double _tmpAmount;
            _tmpAmount = _cursor.getDouble(_cursorIndexOfAmount);
            final String _tmpTransactionType;
            if (_cursor.isNull(_cursorIndexOfTransactionType)) {
              _tmpTransactionType = null;
            } else {
              _tmpTransactionType = _cursor.getString(_cursorIndexOfTransactionType);
            }
            final String _tmpSender;
            if (_cursor.isNull(_cursorIndexOfSender)) {
              _tmpSender = null;
            } else {
              _tmpSender = _cursor.getString(_cursorIndexOfSender);
            }
            final String _tmpReceiver;
            if (_cursor.isNull(_cursorIndexOfReceiver)) {
              _tmpReceiver = null;
            } else {
              _tmpReceiver = _cursor.getString(_cursorIndexOfReceiver);
            }
            final String _tmpPaybillNumber;
            if (_cursor.isNull(_cursorIndexOfPaybillNumber)) {
              _tmpPaybillNumber = null;
            } else {
              _tmpPaybillNumber = _cursor.getString(_cursorIndexOfPaybillNumber);
            }
            final String _tmpTillNumber;
            if (_cursor.isNull(_cursorIndexOfTillNumber)) {
              _tmpTillNumber = null;
            } else {
              _tmpTillNumber = _cursor.getString(_cursorIndexOfTillNumber);
            }
            final String _tmpAccountReference;
            if (_cursor.isNull(_cursorIndexOfAccountReference)) {
              _tmpAccountReference = null;
            } else {
              _tmpAccountReference = _cursor.getString(_cursorIndexOfAccountReference);
            }
            final String _tmpDate;
            if (_cursor.isNull(_cursorIndexOfDate)) {
              _tmpDate = null;
            } else {
              _tmpDate = _cursor.getString(_cursorIndexOfDate);
            }
            final String _tmpTime;
            if (_cursor.isNull(_cursorIndexOfTime)) {
              _tmpTime = null;
            } else {
              _tmpTime = _cursor.getString(_cursorIndexOfTime);
            }
            final Double _tmpBalance;
            if (_cursor.isNull(_cursorIndexOfBalance)) {
              _tmpBalance = null;
            } else {
              _tmpBalance = _cursor.getDouble(_cursorIndexOfBalance);
            }
            final String _tmpRawSmsBody;
            if (_cursor.isNull(_cursorIndexOfRawSmsBody)) {
              _tmpRawSmsBody = null;
            } else {
              _tmpRawSmsBody = _cursor.getString(_cursorIndexOfRawSmsBody);
            }
            final long _tmpReceivedAtMillis;
            _tmpReceivedAtMillis = _cursor.getLong(_cursorIndexOfReceivedAtMillis);
            final int _tmpSyncAttempts;
            _tmpSyncAttempts = _cursor.getInt(_cursorIndexOfSyncAttempts);
            final String _tmpLastError;
            if (_cursor.isNull(_cursorIndexOfLastError)) {
              _tmpLastError = null;
            } else {
              _tmpLastError = _cursor.getString(_cursorIndexOfLastError);
            }
            _item = new PendingTransactionEntity(_tmpId,_tmpTransactionCode,_tmpAmount,_tmpTransactionType,_tmpSender,_tmpReceiver,_tmpPaybillNumber,_tmpTillNumber,_tmpAccountReference,_tmpDate,_tmpTime,_tmpBalance,_tmpRawSmsBody,_tmpReceivedAtMillis,_tmpSyncAttempts,_tmpLastError);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object countPending(final Continuation<? super Integer> $completion) {
    final String _sql = "SELECT COUNT(*) FROM pending_transactions";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Integer>() {
      @Override
      @NonNull
      public Integer call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Integer _result;
          if (_cursor.moveToFirst()) {
            final Integer _tmp;
            if (_cursor.isNull(0)) {
              _tmp = null;
            } else {
              _tmp = _cursor.getInt(0);
            }
            _result = _tmp;
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object existsByCode(final String code, final Continuation<? super Boolean> $completion) {
    final String _sql = "SELECT EXISTS(SELECT 1 FROM pending_transactions WHERE transactionCode = ?)";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    if (code == null) {
      _statement.bindNull(_argIndex);
    } else {
      _statement.bindString(_argIndex, code);
    }
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<Boolean>() {
      @Override
      @NonNull
      public Boolean call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Boolean _result;
          if (_cursor.moveToFirst()) {
            final Integer _tmp;
            if (_cursor.isNull(0)) {
              _tmp = null;
            } else {
              _tmp = _cursor.getInt(0);
            }
            _result = _tmp == null ? null : _tmp != 0;
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getRecent(final int limit,
      final Continuation<? super List<PendingTransactionEntity>> $completion) {
    final String _sql = "SELECT * FROM pending_transactions ORDER BY receivedAtMillis DESC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, limit);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<PendingTransactionEntity>>() {
      @Override
      @NonNull
      public List<PendingTransactionEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfTransactionCode = CursorUtil.getColumnIndexOrThrow(_cursor, "transactionCode");
          final int _cursorIndexOfAmount = CursorUtil.getColumnIndexOrThrow(_cursor, "amount");
          final int _cursorIndexOfTransactionType = CursorUtil.getColumnIndexOrThrow(_cursor, "transactionType");
          final int _cursorIndexOfSender = CursorUtil.getColumnIndexOrThrow(_cursor, "sender");
          final int _cursorIndexOfReceiver = CursorUtil.getColumnIndexOrThrow(_cursor, "receiver");
          final int _cursorIndexOfPaybillNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "paybillNumber");
          final int _cursorIndexOfTillNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "tillNumber");
          final int _cursorIndexOfAccountReference = CursorUtil.getColumnIndexOrThrow(_cursor, "accountReference");
          final int _cursorIndexOfDate = CursorUtil.getColumnIndexOrThrow(_cursor, "date");
          final int _cursorIndexOfTime = CursorUtil.getColumnIndexOrThrow(_cursor, "time");
          final int _cursorIndexOfBalance = CursorUtil.getColumnIndexOrThrow(_cursor, "balance");
          final int _cursorIndexOfRawSmsBody = CursorUtil.getColumnIndexOrThrow(_cursor, "rawSmsBody");
          final int _cursorIndexOfReceivedAtMillis = CursorUtil.getColumnIndexOrThrow(_cursor, "receivedAtMillis");
          final int _cursorIndexOfSyncAttempts = CursorUtil.getColumnIndexOrThrow(_cursor, "syncAttempts");
          final int _cursorIndexOfLastError = CursorUtil.getColumnIndexOrThrow(_cursor, "lastError");
          final List<PendingTransactionEntity> _result = new ArrayList<PendingTransactionEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final PendingTransactionEntity _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpTransactionCode;
            if (_cursor.isNull(_cursorIndexOfTransactionCode)) {
              _tmpTransactionCode = null;
            } else {
              _tmpTransactionCode = _cursor.getString(_cursorIndexOfTransactionCode);
            }
            final double _tmpAmount;
            _tmpAmount = _cursor.getDouble(_cursorIndexOfAmount);
            final String _tmpTransactionType;
            if (_cursor.isNull(_cursorIndexOfTransactionType)) {
              _tmpTransactionType = null;
            } else {
              _tmpTransactionType = _cursor.getString(_cursorIndexOfTransactionType);
            }
            final String _tmpSender;
            if (_cursor.isNull(_cursorIndexOfSender)) {
              _tmpSender = null;
            } else {
              _tmpSender = _cursor.getString(_cursorIndexOfSender);
            }
            final String _tmpReceiver;
            if (_cursor.isNull(_cursorIndexOfReceiver)) {
              _tmpReceiver = null;
            } else {
              _tmpReceiver = _cursor.getString(_cursorIndexOfReceiver);
            }
            final String _tmpPaybillNumber;
            if (_cursor.isNull(_cursorIndexOfPaybillNumber)) {
              _tmpPaybillNumber = null;
            } else {
              _tmpPaybillNumber = _cursor.getString(_cursorIndexOfPaybillNumber);
            }
            final String _tmpTillNumber;
            if (_cursor.isNull(_cursorIndexOfTillNumber)) {
              _tmpTillNumber = null;
            } else {
              _tmpTillNumber = _cursor.getString(_cursorIndexOfTillNumber);
            }
            final String _tmpAccountReference;
            if (_cursor.isNull(_cursorIndexOfAccountReference)) {
              _tmpAccountReference = null;
            } else {
              _tmpAccountReference = _cursor.getString(_cursorIndexOfAccountReference);
            }
            final String _tmpDate;
            if (_cursor.isNull(_cursorIndexOfDate)) {
              _tmpDate = null;
            } else {
              _tmpDate = _cursor.getString(_cursorIndexOfDate);
            }
            final String _tmpTime;
            if (_cursor.isNull(_cursorIndexOfTime)) {
              _tmpTime = null;
            } else {
              _tmpTime = _cursor.getString(_cursorIndexOfTime);
            }
            final Double _tmpBalance;
            if (_cursor.isNull(_cursorIndexOfBalance)) {
              _tmpBalance = null;
            } else {
              _tmpBalance = _cursor.getDouble(_cursorIndexOfBalance);
            }
            final String _tmpRawSmsBody;
            if (_cursor.isNull(_cursorIndexOfRawSmsBody)) {
              _tmpRawSmsBody = null;
            } else {
              _tmpRawSmsBody = _cursor.getString(_cursorIndexOfRawSmsBody);
            }
            final long _tmpReceivedAtMillis;
            _tmpReceivedAtMillis = _cursor.getLong(_cursorIndexOfReceivedAtMillis);
            final int _tmpSyncAttempts;
            _tmpSyncAttempts = _cursor.getInt(_cursorIndexOfSyncAttempts);
            final String _tmpLastError;
            if (_cursor.isNull(_cursorIndexOfLastError)) {
              _tmpLastError = null;
            } else {
              _tmpLastError = _cursor.getString(_cursorIndexOfLastError);
            }
            _item = new PendingTransactionEntity(_tmpId,_tmpTransactionCode,_tmpAmount,_tmpTransactionType,_tmpSender,_tmpReceiver,_tmpPaybillNumber,_tmpTillNumber,_tmpAccountReference,_tmpDate,_tmpTime,_tmpBalance,_tmpRawSmsBody,_tmpReceivedAtMillis,_tmpSyncAttempts,_tmpLastError);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
