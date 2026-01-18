# Task 1: Security Architecture and C4 Diagram Update

## Architectural Solution

To address the security requirements for BionicPRO, we are introducing a **Backend for Frontend (BFF)** pattern using a new service named `bionicpro-auth`.

### Key Components

1.  **bionicpro-auth (BFF Service):**
    *   **Role:** Acts as the entry point for authentication and a reverse proxy for API requests.
    *   **Responsibility:**
        *   Handles the OAuth2/OIDC Authorization Code Flow with PKCE against Keycloak.
        *   Stores `access_token` and `refresh_token` securely (e.g., in-memory or Redis).
        *   Issues a generic Session ID (HTTP-only, Secure, SameSite cookie) to the Frontend.
        *   Proxies requests from Frontend to Backend Services (MES, CRM, Store), replacing the Session Cookie with the Bearer Access Token.
        *   Automatically refreshes tokens using the stored `refresh_token` when the `access_token` expires.
    *   **Benefit:** Tokens are never exposed to the browser (XSS protection).

2.  **Keycloak (Identity Provider):**
    *   **Role:** Central Authentication Server.
    *   **Features:**
        *   **Identity Brokering:** Configured to trust external IdPs (Yandex ID) and connect to User Federation sources (LDAP).
        *   **MFA:** Enforces OTP for users.
        *   **Token Lifecycle:** Short-lived access tokens (< 2 mins), longer-lived refresh tokens.

3.  **Frontend Applications (Store, CRM, MES):**
    *   **Change:** Remove all OIDC client logic (oidc-client-js, etc.).
    *   **New Logic:** Simply check for the presence of the Session Cookie (via a `/me` endpoint on the BFF) and handle 401 errors by redirecting the user to the BFF's `/login` endpoint.

4.  **External Sources:**
    *   **LDAP:** For country-specific representative user data.
    *   **Yandex ID:** For social login / external identity.

### C4 Diagram Updates

#### Context Level
*   **Add:** `External Identity Provider (Yandex ID)` and `Corporate LDAP`.
*   **Relationship:** `Keycloak` syncs with `LDAP` and delegates auth to `Yandex ID`.

#### Container Level
*   **Add:** `Auth Service (bionicpro-auth)` container.
*   **Change Relationships:**
    *   *Old:* Frontend -> (Tokens) -> Backend Services.
    *   *New:* Frontend -> (Session Cookie) -> `bionicpro-auth`.
    *   *New:* `bionicpro-auth` -> (Bearer Token) -> Backend Services (Billing, Orders, MES, CRM).
    *   *New:* `bionicpro-auth` -> (OIDC) -> Keycloak.

## Diagram Description (Textual)

```mermaid
graph TD
    User((User))
    subgraph "BionicPRO System"
        Frontend[Frontend Apps\n(Vue/React)]
        AuthService[bionicpro-auth\n(BFF / Reverse Proxy)]
        Keycloak[Keycloak\n(IdP)]
        Backend[Backend Services\n(Store, CRM, MES)]
    end
    subgraph "External"
        Yandex[Yandex ID]
        LDAP[Country Office LDAP]
    end

    User -- HTTPS --> Frontend
    Frontend -- "1. Login (Redirect)" --> AuthService
    AuthService -- "2. OIDC Code Flow" --> Keycloak
    Keycloak -- "3. Authenticate" --> LDAP
    Keycloak -- "3. Authenticate" --> Yandex
    Keycloak -- "4. Tokens" --> AuthService
    AuthService -- "5. Session Cookie" --> Frontend

    Frontend -- "6. API Req (Cookie)" --> AuthService
    AuthService -- "7. Proxy (Bearer Token)" --> Backend
```
