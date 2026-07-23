package com.mpesaai.assistant.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.text.format.DateFormat
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequest
import androidx.work.WorkManager
import com.mpesaai.assistant.R
import com.mpesaai.assistant.data.AppDatabase
import com.mpesaai.assistant.data.PreferencesManager
import com.mpesaai.assistant.network.AuthRepository
import com.mpesaai.assistant.sync.SyncWorker
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var prefs: PreferencesManager
    private lateinit var adapter: PendingTransactionAdapter
    private var pollingActive = true

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        prefs = PreferencesManager.getInstance(this)

        val toolbar = findViewById<Toolbar>(R.id.toolbar)
        toolbar.title = getString(R.string.app_name)

        val recyclerView = findViewById<RecyclerView>(R.id.recentTransactionsList)
        adapter = PendingTransactionAdapter()
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter

        findViewById<android.widget.TextView>(R.id.linkedUserText).text =
            getString(R.string.linked_as, prefs.linkedUserName ?: prefs.linkedUserId ?: "—")
	findViewById<android.widget.TextView>(R.id.linkedUserText).setOnClickListener {
    startActivity(Intent(this, ChangePasswordActivity::class.java))
    }

        findViewById<android.widget.Button>(R.id.syncNowButton).setOnClickListener { triggerImmediateSync() }
        findViewById<android.widget.Button>(R.id.signOutButton).setOnClickListener { signOut() }

        checkPermissions()
        refreshStatus()
        startPolling()
    }

    override fun onDestroy() {
        super.onDestroy()
        pollingActive = false
    }

    private fun checkPermissions() {
        val permissions = arrayOf(Manifest.permission.RECEIVE_SMS, Manifest.permission.READ_SMS)
        val allGranted = permissions.all {
            ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
        }
        findViewById<View>(R.id.permissionBanner).visibility = if (allGranted) View.GONE else View.VISIBLE
    }

    private fun triggerImmediateSync() {
        val request = OneTimeWorkRequest.Builder(SyncWorker::class.java).build()
        WorkManager.getInstance(this).enqueueUniqueWork(
            SyncWorker.IMMEDIATE_WORK_NAME,
            ExistingWorkPolicy.REPLACE,
            request
        )
    }

    private fun startPolling() {
        lifecycleScope.launch {
            while (pollingActive) {
                refreshStatus()
                delay(5000)
            }
        }
    }

    private fun refreshStatus() {
        lifecycleScope.launch {
            val dao = AppDatabase.getInstance(this@MainActivity).pendingTransactionDao()
            val pendingCount = dao.countPending()
            val recent = dao.getRecent(20)

            findViewById<android.widget.TextView>(R.id.pendingCountText).text =
                resources.getQuantityString(R.plurals.pending_count, pendingCount, pendingCount)

            val now = DateFormat.getTimeFormat(this@MainActivity).format(java.util.Date())
            findViewById<android.widget.TextView>(R.id.lastSyncText).text = getString(R.string.last_checked, now)

            adapter.submitList(recent)
        }
    }

    private fun signOut() {
        AuthRepository(this).logout()
        startActivity(Intent(this, LoginActivity::class.java))
        finish()
    }
}
