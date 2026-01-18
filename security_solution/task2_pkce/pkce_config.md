# Настройка Keycloak для PKCE

Чтобы включить Proof Key for Code Exchange (PKCE) в Keycloak для клиента `bionicpro-backend`:

1.  **Откройте консоль администратора Keycloak.**
2.  **Перейдите в Clients (Клиенты)** и выберите `bionicpro-backend`.
3.  **Вкладка Settings (Настройки):**
    *   **Access Type:** `Confidential` (так как мы используем backend BFF, мы можем использовать секреты клиента, но PKCE обеспечивает дополнительную безопасность) или `Public` (если это чисто SPA, но здесь у нас BFF).
        *   *Примечание:* Даже для конфиденциальных клиентов рекомендуется использовать PKCE.
    *   **Standard Flow Enabled:** `ON`
    *   **Direct Access Grants Enabled:** `OFF` (Отключить вход по паролю)
    *   **Implicit Flow Enabled:** `OFF`
4.  **Advanced Settings (Расширенные настройки) (или "OpenID Connect Compatibility Modes" в старых версиях):**
    *   **Proof Key for Code Exchange Code Challenge Method:** `S256` (Не используйте `plain`).
5.  **Сохраните** конфигурацию.

## Зачем нужен PKCE?
PKCE предотвращает атаки с перехватом кода авторизации. Принудительно используя `S256`, Keycloak гарантирует, что сущность, обменивающая код на токен, является той же самой, которая инициировала запрос.
