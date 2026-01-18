# Keycloak Configuration for PKCE

To enable Proof Key for Code Exchange (PKCE) in Keycloak for the `bionicpro-backend` client:

1.  **Open Keycloak Admin Console.**
2.  **Navigate to Clients** and select `bionicpro-backend`.
3.  **Settings Tab:**
    *   **Access Type:** `Confidential` (since we are using a backend BFF, we can use client secrets, but PKCE provides extra security) or `Public` (if strictly SPA, but here we are BFF).
        *   *Note:* Even for Confidential clients, PKCE is recommended.
    *   **Standard Flow Enabled:** `ON`
    *   **Direct Access Grants Enabled:** `OFF` (Disable password grant)
    *   **Implicit Flow Enabled:** `OFF`
4.  **Advanced Settings (or "OpenID Connect Compatibility Modes" in older versions):**
    *   **Proof Key for Code Exchange Code Challenge Method:** `S256` (Do not use `plain`).
5.  **Save** the configuration.

## Why PKCE?
PKCE prevents authorization code interception attacks. By enforcing `S256`, Keycloak ensures that the entity exchanging the code for a token is the same one that initiated the request.
