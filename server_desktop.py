📄 FILE 5: server_desktop.py
Click "Add file" → "Create new file" → Name it: server_desktop.py → Paste this ENTIRE code:

⚠️ This is LONG - scroll down and make sure you copy EVERYTHING until the very end!

"""
FastAPI server for desktop application using SQLite.
"""
from pathlib import Path
import os

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone, timedelta
import logging
import bcrypt
import jwt
import uuid

from database_sqlite import db

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

JWT_ALGORITHM = "HS256"
JWT_SECRET = "your-secret-key-change-in-production"

# ============ UTILITY FUNCTIONS ============
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user = await db.fetch_one("SELECT * FROM users WHERE id = ?", (payload["sub"],))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        user_dict = dict(user)
        user_dict["_id"] = user_dict["id"]
        user_dict["onboarded"] = bool(user_dict["onboarded"])
        user_dict.pop("password_hash", None)
        return user_dict
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ MODELS ============
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class OnboardingData(BaseModel):
    name: str
    phone: str
    initial_goal: Optional[str] = None

class TransactionCreate(BaseModel):
    type: str
    category: str
    amount: float
    description: Optional[str] = None
    date: datetime

class InvestmentCreate(BaseModel):
    institution_type: str
    institution_name: str
    investment_amount: float
    start_date: datetime
    maturity_date: datetime
    maturity_amount: float
    notes: Optional[str] = None

class CustomInstitutionCreate(BaseModel):
    type: str
    name: str

# ============ AUTH ENDPOINTS ============
@api_router.post("/auth/register")
async def register(data: RegisterRequest, response: Response):
    email = data.email.lower()
    existing = await db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    password_hash = hash_password(data.password)
    
    await db.execute(
        """INSERT INTO users (id, email, password_hash, name, phone, role, onboarded, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, email, password_hash, data.name, data.phone, "user", 0, datetime.now(timezone.utc).isoformat())
    )
    
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=900, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=604800, path="/")
    
    return {"_id": user_id, "email": email, "name": data.name, "phone": data.phone, "role": "user", "onboarded": False}

@api_router.post("/auth/login")
async def login(data: LoginRequest, response: Response):
    email = data.email.lower()
    user = await db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = user["id"]
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=900, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=604800, path="/")
    
    return {"_id": user_id, "email": user["email"], "name": user["name"], "phone": user["phone"], 
            "role": user["role"], "onboarded": bool(user["onboarded"])}

@api_router.get("/auth/me")
async def get_me(request: Request):
    return await get_current_user(request)

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logged out successfully"}

# ============ ONBOARDING ============
@api_router.post("/onboarding")
async def complete_onboarding(data: OnboardingData, request: Request):
    user = await get_current_user(request)
    await db.execute(
        """UPDATE users SET name = ?, phone = ?, initial_goal = ?, onboarded = 1 WHERE id = ?""",
        (data.name, data.phone, data.initial_goal, user["_id"])
    )
    return {"message": "Onboarding completed"}

# ============ TRANSACTIONS ============
@api_router.post("/transactions")
async def create_transaction(data: TransactionCreate, request: Request):
    user = await get_current_user(request)
    trans_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO transactions (id, user_id, type, category, amount, description, date, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (trans_id, user["_id"], data.type, data.category, data.amount, data.description,
         data.date.isoformat(), datetime.now(timezone.utc).isoformat())
    )
    return {"id": trans_id, "user_id": user["_id"], "type": data.type, "category": data.category,
            "amount": data.amount, "description": data.description, "date": data.date.isoformat()}

@api_router.get("/transactions")
async def get_transactions(request: Request):
    user = await get_current_user(request)
    return await db.fetch_all("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user["_id"],))

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, request: Request):
    user = await get_current_user(request)
    await db.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user["_id"]))
    return {"message": "Transaction deleted"}

# ============ INVESTMENTS ============
@api_router.post("/investments")
async def create_investment(data: InvestmentCreate, request: Request):
    user = await get_current_user(request)
    inv_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO investments (id, user_id, institution_type, institution_name,
           investment_amount, start_date, maturity_date, maturity_amount, notes, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (inv_id, user["_id"], data.institution_type, data.institution_name,
         data.investment_amount, data.start_date.isoformat(), data.maturity_date.isoformat(),
         data.maturity_amount, data.notes, datetime.now(timezone.utc).isoformat())
    )
    return {"id": inv_id, "user_id": user["_id"], "institution_type": data.institution_type,
            "institution_name": data.institution_name, "investment_amount": data.investment_amount,
            "start_date": data.start_date.isoformat(), "maturity_date": data.maturity_date.isoformat(),
            "maturity_amount": data.maturity_amount, "notes": data.notes}

@api_router.get("/investments")
async def get_investments(request: Request):
    user = await get_current_user(request)
    return await db.fetch_all("SELECT * FROM investments WHERE user_id = ? ORDER BY start_date DESC", (user["_id"],))

@api_router.delete("/investments/{investment_id}")
async def delete_investment(investment_id: str, request: Request):
    user = await get_current_user(request)
    await db.execute("DELETE FROM investments WHERE id = ? AND user_id = ?", (investment_id, user["_id"]))
    return {"message": "Investment deleted"}

# ============ CUSTOM INSTITUTIONS ============
@api_router.post("/custom-institutions")
async def create_custom_institution(data: CustomInstitutionCreate, request: Request):
    user = await get_current_user(request)
    existing = await db.fetch_one(
        "SELECT * FROM custom_institutions WHERE user_id = ? AND type = ? AND name = ?",
        (user["_id"], data.type, data.name)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Institution already exists")
    
    inst_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO custom_institutions (id, user_id, type, name, created_at) VALUES (?, ?, ?, ?, ?)""",
        (inst_id, user["_id"], data.type, data.name, datetime.now(timezone.utc).isoformat())
    )
    return {"id": inst_id, "user_id": user["_id"], "type": data.type, "name": data.name}

@api_router.get("/custom-institutions")
async def get_custom_institutions(request: Request, type: Optional[str] = None):
    user = await get_current_user(request)
    if type:
        return await db.fetch_all(
            "SELECT * FROM custom_institutions WHERE user_id = ? AND type = ? ORDER BY name",
            (user["_id"], type)
        )
    return await db.fetch_all("SELECT * FROM custom_institutions WHERE user_id = ? ORDER BY name", (user["_id"],))

@api_router.delete("/custom-institutions/{institution_id}")
async def delete_custom_institution(institution_id: str, request: Request):
    user = await get_current_user(request)
    await db.execute("DELETE FROM custom_institutions WHERE id = ? AND user_id = ?", (institution_id, user["_id"]))
    return {"message": "Institution deleted"}

# ============ DASHBOARD STATS ============
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request):
    user = await get_current_user(request)
    transactions = await db.fetch_all("SELECT * FROM transactions WHERE user_id = ?", (user["_id"],))
    investments = await db.fetch_all("SELECT * FROM investments WHERE user_id = ?", (user["_id"],))
    
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    total_invested = sum(inv["investment_amount"] for inv in investments)
    total_maturity = sum(inv["maturity_amount"] for inv in investments)
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "savings": total_income - total_expenses,
        "total_invested": total_invested,
        "total_maturity": total_maturity,
        "net_worth": (total_income - total_expenses) + total_invested
    }

# ============ REPORTS ============
@api_router.get("/reports/data")
async def get_report_data(request: Request):
    user = await get_current_user(request)
    transactions = await db.fetch_all("SELECT * FROM transactions WHERE user_id = ?", (user["_id"],))
    investments = await db.fetch_all("SELECT * FROM investments WHERE user_id = ?", (user["_id"],))
    
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    total_invested = sum(inv["investment_amount"] for inv in investments)
    total_maturity = sum(inv["maturity_amount"] for inv in investments)
    
    return {
        "user": {"name": user["name"], "email": user["email"]},
        "stats": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "savings": total_income - total_expenses,
            "total_invested": total_invested,
            "total_maturity": total_maturity,
            "net_worth": (total_income - total_expenses) + total_invested
        },
        "transactions": transactions,
        "investments": investments
    }

# ============ NOTIFICATIONS ============
@api_router.get("/notifications")
async def get_notifications(request: Request):
    user = await get_current_user(request)
    return await db.fetch_all(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (user["_id"],)
    )

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    user = await get_current_user(request)
    await db.execute("UPDATE notifications SET read = 1 WHERE id = ? AND user_id = ?", (notification_id, user["_id"]))
    return {"message": "Notification marked as read"}

# ============ STARTUP ============
@app.on_event("startup")
async def startup_event():
    await db.connect()
    admin_email = "admin@financeapp.com"
    admin_password = "admin123"
    existing = await db.fetch_one("SELECT * FROM users WHERE email = ?", (admin_email,))
    
    if existing is None:
        user_id = str(uuid.uuid4())
        hashed = hash_password(admin_password)
        await db.execute(
            """INSERT INTO users (id, email, password_hash, name, phone, role, onboarded, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, admin_email, hashed, "Admin", "+919999999999", "admin", 1,
             datetime.now(timezone.utc).isoformat())
        )
        print(f"Admin user created: {admin_email}")
    print(f"Database initialized at: {db.db_path}")

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Finance Manager - Starting Server")
    print("=" * 50)
    print(f"Server: http://localhost:8001")
    print(f"Database: {db.db_path}")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8001)
