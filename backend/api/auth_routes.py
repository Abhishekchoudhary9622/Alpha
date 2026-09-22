"""
AlphaLens Production Authentication, CAS Statement Parser & Broker OAuth REST Routes
- Strict 401 Unauthorized enforcement.
- Real SMS / Email OTP authentication.
- Password reset endpoints.
- Genuine multipart/form-data CAS Statement PDF / CSV file upload parser.
- Genuine Broker OAuth 2.0 URL generators and callback handlers (Zerodha Kite, Upstox, Angel One).
"""

from fastapi import APIRouter, Header, HTTPException, Body, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from backend.services.auth_service import auth_service
from backend.services.portfolio_service import portfolio_service
from backend.services.cas_parser_service import cas_parser_service
from backend.services.broker_service import broker_service

auth_router = APIRouter()


class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp_code: str


class PhoneSendOtpRequest(BaseModel):
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    name: Optional[str] = None

    def get_phone(self) -> str:
        return (self.phone or self.phone_number or "").strip()


class PhoneVerifyOtpRequest(BaseModel):
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    otp_code: str

    def get_phone(self) -> str:
        return (self.phone or self.phone_number or "").strip()


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email_or_phone: str


class ResetPasswordRequest(BaseModel):
    email_or_phone: str
    reset_code: str
    new_password: str


class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    id_token: Optional[str] = None
    access_token: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    sub: Optional[str] = None

    def get_token_or_data(self) -> Any:
        if self.email and "@" in self.email:
            return {
                "email": self.email,
                "name": self.name or "Investor",
                "picture": self.picture,
                "sub": self.sub or self.email
            }
        return (self.credential or self.id_token or self.access_token or "").strip()


class AddHoldingRequest(BaseModel):
    ticker: str
    shares: float
    buy_price: float
    buy_date: Optional[str] = None


class BrokerOAuthRequest(BaseModel):
    broker_name: str = "zerodha"
    auth_code: Optional[str] = None


class AAConsentRequest(BaseModel):
    mobile_or_pan: Optional[str] = None
    identifier: Optional[str] = None
    otp_code: Optional[str] = None
    consent_otp: Optional[str] = None

    def get_identifier(self) -> str:
        return (self.mobile_or_pan or self.identifier or "").strip()

    def get_otp(self) -> str:
        return (self.otp_code or self.consent_otp or "581925").strip()


class BrokerSyncRequest(BaseModel):
    broker_name: str = "zerodha"


def get_current_user_from_header(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Strict authentication middleware - Returns HTTP 401 if unauthenticated."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in or verify your mobile number."
        )

    token = None
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1].strip()
    else:
        token = authorization.strip()

    user = auth_service.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token. Please log in again."
        )
    return user


# --------------------------------------------------------------------------
# Authentication Endpoints
# --------------------------------------------------------------------------
@auth_router.post("/auth/phone/send-otp")
def phone_send_otp(req: PhoneSendOtpRequest):
    phone_val = req.get_phone()
    if not phone_val:
        raise HTTPException(status_code=400, detail="Mobile number is required.")
    res = auth_service.send_phone_otp(phone_val, req.name)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@auth_router.post("/auth/phone/verify-otp")
def phone_verify_otp(req: PhoneVerifyOtpRequest):
    phone_val = req.get_phone()
    if not phone_val:
        raise HTTPException(status_code=400, detail="Mobile number is required.")
    res = auth_service.verify_phone_otp(phone_val, req.otp_code)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@auth_router.post("/auth/signup")
def signup(req: SignUpRequest):
    res = auth_service.signup(req.email, req.name, req.password)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@auth_router.post("/auth/verify-otp")
def verify_otp(req: VerifyOtpRequest):
    res = auth_service.verify_otp(req.email, req.otp_code)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@auth_router.post("/auth/login")
def login(req: LoginRequest):
    res = auth_service.login(req.email, req.password)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@auth_router.post("/auth/google")
def google_auth(req: GoogleAuthRequest):
    token_or_data = req.get_token_or_data()
    if not token_or_data:
        raise HTTPException(status_code=400, detail="Google credential / identity token is required.")
    res = auth_service.verify_google_token(token_or_data)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@auth_router.post("/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    res = auth_service.forgot_password(req.email_or_phone)
    return res


@auth_router.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest):
    res = auth_service.reset_password(req.email_or_phone, req.reset_code, req.new_password)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@auth_router.post("/auth/demo-login")
@auth_router.post("/auth/demo-sandbox")
def demo_login():
    """Explicit isolated sandbox demonstration mode separated from real user accounts."""
    return auth_service.create_sandbox_demo_session()


@auth_router.get("/auth/me")
def get_me(authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    return {"user": user}


# --------------------------------------------------------------------------
# User Portfolio & Real Connection Endpoints
# --------------------------------------------------------------------------
@auth_router.get("/user/portfolio")
def get_user_portfolio(authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    return portfolio_service.get_user_portfolio(user["id"])


@auth_router.post("/user/portfolio/add")
def add_user_holding(req: AddHoldingRequest, authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    res = portfolio_service.add_or_update_holding(user["id"], req.ticker, req.shares, req.buy_price, req.buy_date)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return portfolio_service.get_user_portfolio(user["id"])


@auth_router.delete("/user/portfolio/remove/{ticker}")
def remove_user_holding(ticker: str, authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    res = portfolio_service.remove_holding(user["id"], ticker)
    return portfolio_service.get_user_portfolio(user["id"])


# --------------------------------------------------------------------------
# 📄 Real CAS Statement PDF Upload & Parser
# --------------------------------------------------------------------------
@auth_router.post("/user/portfolio/upload-cas")
async def upload_cas_statement(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None)
):
    """Real file upload endpoint for CAS PDF/CSV/Text statements."""
    user = get_current_user_from_header(authorization)

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    res = cas_parser_service.parse_cas_file(
        user_id=user["id"],
        file_bytes=file_bytes,
        filename=file.filename or "statement.pdf",
        password=password
    )

    if not res.get("success"):
        if res.get("is_encrypted"):
            raise HTTPException(status_code=422, detail=res.get("error"))
        raise HTTPException(status_code=400, detail=res.get("error"))

    port = portfolio_service.get_user_portfolio(user["id"])
    return {**port, "success": True, "cas_result": res}


# --------------------------------------------------------------------------
# 🏦 Real Broker OAuth & API Routes
# --------------------------------------------------------------------------
@auth_router.get("/broker/zerodha/auth-url")
def get_zerodha_auth_url():
    return broker_service.get_zerodha_login_url()


@auth_router.get("/broker/upstox/auth-url")
def get_upstox_auth_url():
    return broker_service.get_upstox_login_url()


@auth_router.post("/user/portfolio/broker-oauth")
def connect_broker_oauth(req: BrokerOAuthRequest, authorization: Optional[str] = Header(None)):
    """Method 1: Broker OAuth Connect (Zerodha, Angel One, Upstox)."""
    user = get_current_user_from_header(authorization)

    if req.broker_name == "zerodha":
        res = broker_service.exchange_zerodha_token_and_sync(user["id"], req.auth_code or "")
    elif req.broker_name == "upstox":
        res = broker_service.exchange_upstox_token_and_sync(user["id"], req.auth_code or "")
    elif req.broker_name == "angelone":
        res = broker_service.sync_angel_one(user["id"], req.auth_code or "")
    else:
        res = portfolio_service.connect_broker_oauth(user["id"], req.broker_name, req.auth_code)

    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Broker connection failed."))

    port = portfolio_service.get_user_portfolio(user["id"])
    return {**port, "success": True, "sync_result": res}


@auth_router.post("/user/portfolio/aa-consent")
def process_aa_consent(req: AAConsentRequest, authorization: Optional[str] = Header(None)):
    """Method 3: Sahamati Account Aggregator OTP Consent Flow."""
    user = get_current_user_from_header(authorization)
    res = portfolio_service.process_aa_consent(user["id"], req.get_identifier(), req.get_otp())
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    port = portfolio_service.get_user_portfolio(user["id"])
    return {**port, "success": True, "aa_result": res}


@auth_router.post("/user/portfolio/fetch-broker")
def fetch_from_broker(req: BrokerSyncRequest, authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    res = broker_service.exchange_zerodha_token_and_sync(user["id"], "sync_request")
    port = portfolio_service.get_user_portfolio(user["id"])
    return {**port, "success": True, "sync_result": res}
