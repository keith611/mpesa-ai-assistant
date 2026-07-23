package com.mpesaai.assistant

import android.app.Application
import com.mpesaai.assistant.sync.SyncScheduler

class MpesaApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        SyncScheduler.schedulePeriodicSync(this)
    }
}
