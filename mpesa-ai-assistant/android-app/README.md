# M-Pesa AI Assistant — Android SMS Reader (Phase 5)

Kotlin Android app that reads incoming M-Pesa confirmation SMS, parses them
into structured transactions, and syncs them to the FastAPI backend —
without ever touching the Excel files directly, and without interfering
with the user's normal Messages app.

## How it works

```
Incoming SMS → SmsReceiver → MpesaSmsParser → Room (offline queue) → SyncWorker → Backend /transactions/ingest
```

1. **SmsReceiver** listens for `SMS_RECEIVED_ACTION`, filters for senders
   containing "MPESA", and never calls `abortBroadcast()` — the stock
   Messages app still receives every SMS exactly as before.
2. **MpesaSmsParser** parses the six main M-Pesa message shapes: Send Money,
   Buy Goods (Till), Paybill, Receive, Withdraw, and Deposit. Unmatched
   messages are safely skipped rather than guessed at.
3. Parsed transactions are inserted into a **Room** database with a unique
   index on the M-Pesa transaction code — a duplicate SMS is silently
   ignored at the database level before it ever reaches the network.
4. **SyncWorker** (via WorkManager) drains the queue to the backend's
   device-key-protected `/transactions/ingest` endpoint. It runs immediately
   after each new SMS, and periodically every 15 minutes with a
   `NetworkType.CONNECTED` constraint — so anything queued while offline
   syncs automatically once connectivity returns. A `409 Conflict` from the
   backend (meaning it already has that transaction) is treated as success
   and removed from the local queue, rather than retried forever.
5. Auth tokens are stored in **EncryptedSharedPreferences**, never in
   plaintext.

## Project structure

```
android-app/
  app/src/main/java/com/mpesaai/assistant/
    MpesaApplication.kt        — schedules periodic sync on app start
    ui/                        — Splash, Login, Main activities + adapter
    sms/
      SmsReceiver.kt           — intercepts incoming SMS
      BootReceiver.kt          — reschedules sync after device reboot
      MpesaSmsParser.kt        — the parsing logic (regex-based, no AI)
    data/
      PreferencesManager.kt    — encrypted token/settings storage
      AppDatabase.kt / PendingTransactionEntity.kt / PendingTransactionDao.kt
    network/
      ApiService.kt, RetrofitClient.kt, AuthRepository.kt, dto/
    sync/
      SyncWorker.kt, SyncScheduler.kt
  app/src/main/res/            — layouts, strings, colors, adaptive icon
```

## Setup (Android Studio)

1. Open the `android-app/` folder in Android Studio (Iguana or later). It
   will download Gradle and all dependencies on first sync — this requires
   network access, which wasn't available in the sandbox this was built in,
   so this hasn't been build-verified end to end. Every `.kt` file was
   checked for balanced braces and correct imports, every `.xml` file was
   validated as well-formed, and the SMS parsing regexes were verified
   against real M-Pesa message samples in a Python port of the same logic
   — but `./gradlew build` is worth running as your first step.
2. Point the app at your backend. Two ways:
   - **Emulator against your laptop's backend**: no changes needed —
     `10.0.2.2` is the emulator's built-in alias for your host machine's
     `localhost`, already set as the default in `app/build.gradle`.
   - **Physical device**: change `API_BASE_URL` in `app/build.gradle` to
     your backend's LAN IP (e.g. `http://192.168.1.50:8000/api/v1/`), and
     add that IP to `network_security_config.xml` if it's plain HTTP.
3. Set `DEVICE_API_KEY` in `app/build.gradle` to match your backend's
   `.env` `DEVICE_API_KEY` exactly — this is the shared secret that lets
   the app post transactions without a user JWT.
4. Run on an emulator or physical device (min SDK 26 / Android 8.0+).

## Testing without a real M-Pesa SMS

On an emulator, you can inject a fake SMS from your computer's terminal:

```bash
adb emu sms send MPESA "QAX1B2C3D4 Confirmed. Ksh500.00 sent to JOHN DOE 254712345678 on 2/7/26 at 2:30 PM. New M-PESA balance is Ksh4,500.00."
```

Open the app, sign in with an account already registered on the backend
(e.g. via `python scripts/create_super_admin.py` or the WhatsApp/API
registration flow), grant SMS permissions, then send the fake SMS. It
should appear in the "Recent transactions" list within a few seconds and
show up in the backend's `Transactions.xlsx` and the admin dashboard.

## Known limitations to be aware of

- M-Pesa message wording can vary slightly by carrier config and country
  (this was written against the standard Kenyan Safaricom format). If a
  real message doesn't parse, it's logged and skipped — worth checking
  `MpesaSmsParser` against your actual message samples and adjusting the
  regexes if needed.
- The device links to exactly one backend User ID at a time (whoever is
  signed in). For a shared/family phone receiving M-Pesa messages for
  multiple people, each transaction is attributed to whoever is currently
  signed in on that device.
