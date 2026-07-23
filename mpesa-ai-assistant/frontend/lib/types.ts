export type Role = "SUPER_ADMIN" | "ADMIN" | "SUPPORT" | "USER";
export type UserStatus = "ACTIVE" | "SUSPENDED" | "PENDING" | "DELETED";

export interface AppUser {
  "User ID": string;
  "Full Name": string;
  "Phone Number": string;
  "WhatsApp Number": string;
  Role: Role;
  Status: UserStatus;
  "Registration Date": string;
  "Last Activity": string;
}

export interface Transaction {
  "Transaction ID": string;
  "User ID": string;
  "Transaction Code": string;
  Amount: number;
  "Transaction Type": string;
  Sender: string;
  Receiver: string;
  "Paybill Number": string;
  "Till Number": string;
  "Account Reference": string;
  Date: string;
  Time: string;
  Category: string;
  Balance: number | null;
  Timestamp: string;
  Source: string;
}

export interface Overview {
  total_users: number;
  active_users: number;
  new_users_today: number;
  total_transactions: number;
  total_income: number;
  total_expenses: number;
}

export interface PaginatedUsers {
  total: number;
  page: number;
  page_size: number;
  users: AppUser[];
}

export interface PaginatedTransactions {
  total: number;
  page: number;
  page_size: number;
  transactions: Transaction[];
}

export interface SystemLog {
  "Log ID": string;
  Event: string;
  Timestamp: string;
  Status: string;
  Description: string;
  Actor: string;
}

export interface BackupSnapshot {
  tier: string;
  snapshot: string;
  path: string;
  files: string[];
  size_bytes: number;
}

export interface CategoryRule {
  "Rule ID": string;
  Keyword: string;
  Category: string;
  Priority: number;
  Active: boolean;
  "Updated By": string;
  "Updated At": string;
}

export interface MonthlyReport {
  "Report ID": string;
  "User ID": string;
  Month: string;
  "Total Income": number;
  "Total Expense": number;
  Net: number;
  "Generated At": string;
}
