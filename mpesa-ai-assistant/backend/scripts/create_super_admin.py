"""
One-time CLI script to create the first SUPER_ADMIN account.
Run manually from the backend/ directory: python scripts/create_super_admin.py

This is intentionally NOT an API endpoint — role escalation to SUPER_ADMIN
must never be self-service over HTTP.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from getpass import getpass
from app.db_engine import users as user_engine


def main():
    print("=== Create SUPER_ADMIN account ===")
    full_name = input("Full name: ").strip()
    phone_number = input("Phone number (e.g. 254712345678): ").strip()
    whatsapp_number = input("WhatsApp number (Enter to reuse phone number): ").strip() or phone_number
    password = getpass("Password (min 8 chars): ")
    confirm = getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match. Aborted.")
        return
    if len(password) < 8:
        print("Password must be at least 8 characters. Aborted.")
        return

    try:
        user = user_engine.create_user(
            full_name=full_name,
            phone_number=phone_number,
            whatsapp_number=whatsapp_number,
            password=password,
            role="SUPER_ADMIN",
        )
        print(f"\nSUPER_ADMIN created: {user['User ID']} ({user['Phone Number']})")
    except user_engine.DuplicateUserError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
