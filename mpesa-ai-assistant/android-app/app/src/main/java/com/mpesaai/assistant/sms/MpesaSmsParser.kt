package com.mpesaai.assistant.sms

import java.text.SimpleDateFormat
import java.util.Locale

/**
 * Parses Safaricom M-Pesa confirmation SMS into structured transaction data.
 *
 * M-Pesa message formats vary by transaction type but share a recognizable
 * shape: a leading transaction code, a fixed verb ("Confirmed", "You have
 * received"...), an amount, one or two counterparties, a date/time, and a
 * trailing "New M-PESA balance is ...". This parser handles the six most
 * common formats. Unmatched messages are safely ignored (return null) rather
 * than guessed at — a wrong parse is worse than a skipped message, since the
 * user can still see the original SMS in their normal messages app.
 */
data class ParsedTransaction(
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
)

object MpesaSmsParser {

    // Safaricom's M-Pesa alerts always come from a short alphanumeric sender ID
    // containing "MPESA" (case varies by region/carrier config).
    fun isMpesaSender(sender: String?): Boolean {
        if (sender == null) return false
        return sender.uppercase(Locale.US).contains("MPESA")
    }

    private val CODE_REGEX = Regex("""^([A-Z0-9]{10})\s""")
    private val AMOUNT_REGEX = Regex("""Ksh([\d,]+\.\d{2})""")
    private val BALANCE_REGEX = Regex("""balance is Ksh([\d,]+\.\d{2})""")
    private val DATE_TIME_REGEX = Regex("""on (\d{1,2}/\d{1,2}/\d{2,4}) at (\d{1,2}:\d{2} ?[APMapm]{2})""")

    fun parse(body: String): ParsedTransaction? {
        val text = body.trim().replace("\n", " ").replace(Regex("\\s+"), " ")
        val code = CODE_REGEX.find(text)?.groupValues?.get(1) ?: return null
        val amount = AMOUNT_REGEX.find(text)?.groupValues?.get(1)?.replace(",", "")?.toDoubleOrNull() ?: return null
        val balance = BALANCE_REGEX.find(text)?.groupValues?.get(1)?.replace(",", "")?.toDoubleOrNull()
        val (date, time) = parseDateTime(text)

        return when {
            // "Confirmed. Ksh500.00 sent to JOHN DOE 254712345678 for account 12345
            //  on 2/7/26 at 2:30 PM. New M-PESA balance is Ksh4,500.00..."
            text.contains(" sent to ") -> {
                val receiver = Regex("""sent to ([A-Za-z .]+?)\s+(?:\d{9,}|for account|on )""").find(text)?.groupValues?.get(1)?.trim() ?: ""
                val accountRef = Regex("""for account (\S+)""").find(text)?.groupValues?.get(1) ?: ""
                ParsedTransaction(code, amount, "SEND", "", receiver, "", "", accountRef, date, time, balance)
            }

            // "Confirmed. Ksh1,000.00 paid to NAIVAS SUPERMARKET. on 2/7/26 at 9:00 AM.
            //  New M-PESA balance is Ksh..."  (Buy Goods / Till)
            text.contains(" paid to ") && !text.contains("Paybill") -> {
                val receiver = Regex("""paid to ([A-Za-z0-9 .&'-]+?)\.?\s+on """).find(text)?.groupValues?.get(1)?.trim()
                    ?: Regex("""paid to ([A-Za-z0-9 .&'-]+)""").find(text)?.groupValues?.get(1)?.trim() ?: ""
                val till = Regex("""Till Number[:\s]+(\d+)""").find(text)?.groupValues?.get(1) ?: ""
                ParsedTransaction(code, amount, "TILL", "", receiver, "", till, "", date, time, balance)
            }

            // "Confirmed. Ksh2,500.00 paid to NAIROBI WATER COMPANY for account 998877
            //  on 2/7/26 at 9:00 AM." (Paybill)
            text.contains("Paybill") || (text.contains(" paid to ") && text.contains("for account")) -> {
                val receiver = Regex("""paid to ([A-Za-z0-9 .&'-]+?) for account""").find(text)?.groupValues?.get(1)?.trim() ?: ""
                val accountRef = Regex("""for account (\S+)""").find(text)?.groupValues?.get(1) ?: ""
                val paybill = Regex("""(?:Paybill|Business [Nn]umber)[:\s]+(\d+)""").find(text)?.groupValues?.get(1) ?: ""
                ParsedTransaction(code, amount, "PAYBILL", "", receiver, paybill, "", accountRef, date, time, balance)
            }

            // "Confirmed. You have received Ksh30,000.00 from EMPLOYER LTD 254700111222
            //  on 2/7/26 at 8:00 AM. New M-PESA balance is Ksh..."
            text.contains("received Ksh") -> {
                val sender = Regex("""from ([A-Za-z .]+?)\s+(?:\d{9,}|on )""").find(text)?.groupValues?.get(1)?.trim() ?: ""
                ParsedTransaction(code, amount, "RECEIVE", sender, "", "", "", "", date, time, balance)
            }

            // "Confirmed. Ksh2,000.00 withdrawn from ABC AGENT 12345 - NAIROBI CBD
            //  on 2/7/26 at 3:00 PM. New M-PESA balance is Ksh..."
            text.contains("withdrawn") -> {
                val agent = Regex("""withdrawn from ([A-Za-z0-9 .&'-]+?)\s+on """).find(text)?.groupValues?.get(1)?.trim() ?: ""
                ParsedTransaction(code, amount, "WITHDRAW", "", agent, "", "", "", date, time, balance)
            }

            // "Confirmed. Ksh5,000.00 deposited to your M-PESA account on 2/7/26 at 10:00 AM.
            //  New M-PESA balance is Ksh..."
            text.contains("deposited") -> {
                ParsedTransaction(code, amount, "DEPOSIT", "", "", "", "", "", date, time, balance)
            }

            else -> null
        }
    }

    private fun parseDateTime(text: String): Pair<String, String> {
        val match = DATE_TIME_REGEX.find(text) ?: return Pair("", "")
        val rawDate = match.groupValues[1]
        val rawTime = match.groupValues[2].uppercase(Locale.US).replace(" ", "")

        val isoDate = try {
            val inputFormats = listOf("d/M/yy", "d/M/yyyy", "dd/MM/yy", "dd/MM/yyyy")
            var parsedDate: java.util.Date? = null
            for (fmt in inputFormats) {
                try {
                    parsedDate = SimpleDateFormat(fmt, Locale.US).parse(rawDate)
                    if (parsedDate != null) break
                } catch (_: Exception) { }
            }
            parsedDate?.let { SimpleDateFormat("yyyy-MM-dd", Locale.US).format(it) } ?: rawDate
        } catch (e: Exception) {
            rawDate
        }

        val isoTime = try {
            val parsedTime = SimpleDateFormat("h:mma", Locale.US).parse(rawTime)
            parsedTime?.let { SimpleDateFormat("HH:mm:ss", Locale.US).format(it) } ?: rawTime
        } catch (e: Exception) {
            rawTime
        }

        return Pair(isoDate, isoTime)
    }
}
