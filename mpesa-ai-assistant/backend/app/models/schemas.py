"""
Pydantic models for request validation and response shaping.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------- Auth ----------

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=9, max_length=15)
    whatsapp_number: str = Field(..., min_length=9, max_length=15)
    password: str = Field(..., min_length=8)

    @field_validator("phone_number", "whatsapp_number")
    @classmethod
    def digits_only(cls, v: str) -> str:
        cleaned = v.replace("+", "").replace(" ", "")
        if not cleaned.isdigit():
            raise ValueError("Phone numbers must contain only digits (with optional leading +)")
        return cleaned


class LoginRequest(BaseModel):
    phone_number: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------- Users ----------

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    user_id: str = Field(alias="User ID")
    full_name: str = Field(alias="Full Name")
    phone_number: str = Field(alias="Phone Number")
    whatsapp_number: str = Field(alias="WhatsApp Number")
    role: str = Field(alias="Role")
    status: str = Field(alias="Status")
    registration_date: str = Field(alias="Registration Date")
    last_activity: str = Field(alias="Last Activity")

    class Config:
        populate_by_name = True


# ---------- Transactions ----------

class TransactionCreateRequest(BaseModel):
    user_id: str
    transaction_code: str
    amount: float = Field(..., ge=0)
    transaction_type: str
    sender: Optional[str] = ""
    receiver: Optional[str] = ""
    paybill_number: Optional[str] = ""
    till_number: Optional[str] = ""
    account_reference: Optional[str] = ""
    date: Optional[str] = ""
    time: Optional[str] = ""
    balance: Optional[float] = None
    source: Optional[str] = "SMS"


class TransactionSearchRequest(BaseModel):
    user_id: Optional[str] = None
    keyword: Optional[str] = None
    category: Optional[str] = None
    transaction_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    page: int = 1
    page_size: int = 50


# ---------- WhatsApp ----------

class WhatsAppInboundMessage(BaseModel):
    from_number: str
    message_text: str


# ---------- Category rules ----------

class CategoryRuleRequest(BaseModel):
    keyword: str
    category: str
    priority: int = 5
