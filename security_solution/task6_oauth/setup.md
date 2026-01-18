# Setting up Yandex ID (OAuth 2.0) in Keycloak

To allow users to log in with their Yandex account via Identity Brokering:

## 1. Create an OAuth App in Yandex
1.  Go to [Yandex OAuth](https://oauth.yandex.ru/).
2.  Create a new client.
3.  **Permissions:** Select `yandex:avatar:read`, `login:email`, `login:info`, etc.
4.  **Callback URL:** You need the Keycloak callback URL (see below).
    *   Format: `http://<keycloak-host>/realms/<realm-name>/broker/yandex/endpoint`
5.  Save the `Client ID` and `Client Secret`.

## 2. Configure Keycloak Identity Provider
1.  **Log in to Keycloak Admin Console.**
2.  **Navigate to Identity Providers.**
3.  **Add Provider:** Select `User-defined` (OpenID Connect v1.0) or `Yandex` (if available in your Keycloak version's list).
    *   *Note:* Standard OIDC often works better if Yandex is not pre-listed.
4.  **Configuration:**
    *   **Alias:** `yandex`
    *   **Display Name:** `Yandex ID`
    *   **Authorization URL:** `https://oauth.yandex.ru/authorize`
    *   **Token URL:** `https://oauth.yandex.ru/token`
    *   **Client ID:** (From Step 1)
    *   **Client Secret:** (From Step 1)
    *   **Client Authentication:** `Client secret sent as post` (usually).
5.  **Mappers (Optional but recommended):**
    *   Map `email` to `user.email`.
    *   Map `first_name`, `last_name`.
6.  **Save.**

## 3. Testing
1.  Go to the application login page.
2.  You should see a "Yandex ID" button.
3.  Clicking it redirects to Yandex.
4.  After auth, Yandex redirects back to Keycloak.
5.  **User Profile:** Keycloak will prompt the user to review/update their profile (First Login Flow) unless configured to "Auto Link".
6.  **Data Persistence:** The user profile is stored in Keycloak's database.
