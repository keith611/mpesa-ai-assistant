package com.mpesaai.assistant.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.mpesaai.assistant.sync.SyncScheduler

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            SyncScheduler.schedulePeriodicSync(context.applicationContext)
        }
    }
}
