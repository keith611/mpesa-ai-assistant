"use client";

import { Transaction } from "@/lib/types";
import { CategoryBadge } from "@/components/ui/Badge";
import { formatDateTime, formatMoney } from "@/lib/utils";

interface Props {
  transaction: Transaction;
  onClose: () => void;
}

export default function TransactionDetailModal({ transaction: t, onClose }: Props) {
  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-surface rounded-card border border-border w-full max-w-lg p-6 max-h-[85vh] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="font-display font-semibold text-[15px]">{t["Transaction Type"]}</div>
            <div className="text-xs text-ink-secondary table-figure mt-0.5">{t["Transaction Code"]}</div>
          </div>
          <CategoryBadge category={t.Category} />
        </div>

        <div className="text-2xl font-mono font-medium text-ink mb-5">{formatMoney(t.Amount)}</div>

        <div className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
          <div>
            <div className="text-xs text-ink-secondary mb-0.5">Sender</div>
            <div className="text-ink">{t.Sender || "—"}</div>
          </div>
          <div>
            <div className="text-xs text-ink-secondary mb-0.5">Receiver</div>
            <div className="text-ink">{t.Receiver || "—"}</div>
          </div>
          <div>
            <div className="text-xs text-ink-secondary mb-0.5">Date & time</div>
            <div className="text-ink table-figure">{formatDateTime(t.Timestamp)}</div>
          </div>
          <div>
            <div className="text-xs text-ink-secondary mb-0.5">Balance after</div>
            <div className="text-ink table-figure">{t.Balance != null ? formatMoney(t.Balance) : "—"}</div>
          </div>
          {t["Paybill Number"] && (
            <div>
              <div className="text-xs text-ink-secondary mb-0.5">Paybill</div>
              <div className="text-ink table-figure">{t["Paybill Number"]}</div>
            </div>
          )}
          {t["Till Number"] && (
            <div>
              <div className="text-xs text-ink-secondary mb-0.5">Till</div>
              <div className="text-ink table-figure">{t["Till Number"]}</div>
            </div>
          )}
          {t["Account Reference"] && (
            <div>
              <div className="text-xs text-ink-secondary mb-0.5">Account reference</div>
              <div className="text-ink table-figure">{t["Account Reference"]}</div>
            </div>
          )}
          <div>
            <div className="text-xs text-ink-secondary mb-0.5">Source</div>
            <div className="text-ink">{t.Source}</div>
          </div>
          <div>
            <div className="text-xs text-ink-secondary mb-0.5">User ID</div>
            <div className="text-ink table-figure">{t["User ID"]}</div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full h-9 mt-6 rounded-lg border border-border text-sm font-medium hover:bg-canvas"
        >
          Close
        </button>
      </div>
    </div>
  );
}
