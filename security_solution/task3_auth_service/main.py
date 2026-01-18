import os
import secrets
import time
import logging
import hashlib
import base64
from typing import Dict, Optional
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from keycloak import KeycloakOpenID
import httpx

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="bionicpro-auth")

# Конфигурация (Переменные окружения)
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080/auth/")
REALM_NAME = os.getenv("REALM_NAME", "bionicpro")
CLIENT_ID = os.getenv("CLIENT_ID", "bionicpro-backend")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "secret")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://backend-service:8080")

# Клиент Keycloak
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=CLIENT_ID,
    realm_name=REALM_NAME,
    client_secret_key=CLIENT_SECRET,
    verify=False
)

# Хранилища в оперативной памяти (In-Memory Stores)
# 1. Хранилище сессий: session_id -> {tokens, expiry}
session_store: Dict[str, dict] = {}
# 2. Хранилище ожидающих авторизаций (для PKCE): state -> {code_verifier, created_at}
pending_auths: Dict[str, dict] = {}

# Константы
SESSION_COOKIE_NAME = "bionic_session"
SESSION_DURATION = 3600
AUTH_TIMEOUT = 300 # 5 минут на завершение входа

def create_session(token_info: dict) -> str:
    session_id = secrets.token_urlsafe(32)
    session_store[session_id] = {
        "access_token": token_info["access_token"],
        "refresh_token": token_info.get("refresh_token"), # может отсутствовать, если не настроен
        "expires_at": time.time() + token_info["expires_in"],
        "refresh_expires_at": time.time() + token_info.get("refresh_expires_in", 0)
    }
    return session_id

def rotate_session(old_session_id: str) -> Optional[str]:
    """Задача 3.12: Ротация сессии"""
    if old_session_id in session_store:
        data = session_store.pop(old_session_id)
        new_session_id = secrets.token_urlsafe(32)
        session_store[new_session_id] = data
        return new_session_id
    return None

# Вспомогательные функции PKCE
def generate_code_verifier():
    token = secrets.token_urlsafe(32)
    return token[:128]

def generate_code_challenge(verifier: str):
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip('=')

@app.get("/login")
async def login():
    """Перенаправляет в Keycloak с использованием PKCE."""
    # 1. Генерация данных PKCE
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    state = secrets.token_urlsafe(16)

    # 2. Сохранение Verifier, привязанного к State
    pending_auths[state] = {
        "code_verifier": code_verifier,
        "created_at": time.time()
    }

    # 3. Очистка старых ожидающих авторизаций
    current_time = time.time()
    for s in list(pending_auths.keys()):
        if current_time - pending_auths[s]["created_at"] > AUTH_TIMEOUT:
            del pending_auths[s]

    # 4. Генерация URL авторизации с PKCE
    # Примечание: python-keycloak может не поддерживать 'code_challenge' в auth_url явно во всех версиях через kwargs,
    # но мы можем добавить их вручную.
    auth_url = keycloak_openid.auth_url(
        redirect_uri="http://localhost:8000/callback",
        scope="openid profile email",
        state=state
    )
    # Добавляем параметры PKCE вручную
    auth_url += f"&code_challenge={code_challenge}&code_challenge_method=S256"

    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(code: str, state: str, response: Response):
    """Обменивает код на токены, используя PKCE verifier."""

    # 1. Валидация State
    if state not in pending_auths:
        raise HTTPException(status_code=400, detail="Invalid state or session expired")

    auth_data = pending_auths.pop(state)
    code_verifier = auth_data["code_verifier"]

    try:
        # 2. Обмен кода и Verifier на токены
        # Метод token() в python-keycloak поддерживает аргумент code_verifier
        token_info = keycloak_openid.token(
            grant_type='authorization_code',
            code=code,
            redirect_uri="http://localhost:8000/callback",
            code_verifier=code_verifier
        )

        # 3. Создание сессии
        session_id = create_session(token_info)

        # 4. Установка Cookie
        response = RedirectResponse(url="/")
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=SESSION_DURATION
        )
        return response
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        if not session_id or session_id not in session_store:
             return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        session_data = session_store[session_id]

        # Логика обновления (Refresh)
        if time.time() > session_data["expires_at"] - 10:
            try:
                if not session_data.get("refresh_token"):
                     raise Exception("No refresh token")

                logger.info("Refreshing token...")
                new_token_info = keycloak_openid.refresh_token(session_data["refresh_token"])

                session_data["access_token"] = new_token_info["access_token"]
                session_data["refresh_token"] = new_token_info.get("refresh_token", session_data["refresh_token"])
                session_data["expires_at"] = time.time() + new_token_info["expires_in"]
                session_store[session_id] = session_data
            except Exception as e:
                logger.error(f"Refresh failed: {e}")
                del session_store[session_id]
                return JSONResponse(status_code=401, content={"detail": "Session expired"})

        # Ротация сессии
        new_session_id = rotate_session(session_id)
        if new_session_id:
             session_data = session_store[new_session_id] # Обновляем ссылку

        request.state.access_token = session_data["access_token"]

        response = await call_next(request)

        if new_session_id:
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=new_session_id,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=SESSION_DURATION
            )
        return response

    return await call_next(request)

@app.api_route("/api/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path_name: str, request: Request):
    if not hasattr(request.state, "access_token"):
         raise HTTPException(status_code=401, detail="Unauthorized")

    token = request.state.access_token

    async with httpx.AsyncClient() as client:
        url = f"{BACKEND_BASE_URL}/{path_name}"
        headers = dict(request.headers)
        headers.pop("host", None)
        headers["Authorization"] = f"Bearer {token}"

        try:
            proxy_resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body()
            )
            return Response(
                content=proxy_resp.content,
                status_code=proxy_resp.status_code,
                headers=dict(proxy_resp.headers)
            )
        except httpx.RequestError as exc:
             raise HTTPException(status_code=502, detail=f"Backend connection failed: {exc}")

@app.get("/health")
def health():
    return {"status": "ok"}
