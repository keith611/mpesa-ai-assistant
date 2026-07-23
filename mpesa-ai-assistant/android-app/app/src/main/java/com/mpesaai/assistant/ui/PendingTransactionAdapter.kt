package com.mpesaai.assistant.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.mpesaai.assistant.R
import com.mpesaai.assistant.data.PendingTransactionEntity
import java.util.Locale

class PendingTransactionAdapter : RecyclerView.Adapter<PendingTransactionAdapter.ViewHolder>() {

    private var items: List<PendingTransactionEntity> = emptyList()

    fun submitList(newItems: List<PendingTransactionEntity>) {
        items = newItems
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, position: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_pending_transaction, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val typeText: TextView = itemView.findViewById(R.id.itemType)
        private val amountText: TextView = itemView.findViewById(R.id.itemAmount)
        private val counterpartyText: TextView = itemView.findViewById(R.id.itemCounterparty)
        private val statusText: TextView = itemView.findViewById(R.id.itemStatus)

        fun bind(entity: PendingTransactionEntity) {
            typeText.text = entity.transactionType
            amountText.text = String.format(Locale.US, "KES %,.2f", entity.amount)
            val counterparty = entity.receiver.ifBlank { entity.sender }.ifBlank { "—" }
            counterpartyText.text = counterparty
            statusText.text = if (entity.syncAttempts > 0) {
                "Waiting to sync · ${entity.syncAttempts} attempt(s)"
            } else {
                "Waiting to sync"
            }
        }
    }
}
