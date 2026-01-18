# Настройка Яндекс ID (OAuth 2.0) в Keycloak

Чтобы разрешить пользователям входить с учетной записью Яндекс через Identity Brokering:

## 1. Создание приложения OAuth в Яндекс
1.  Перейдите в [Яндекс OAuth](https://oauth.yandex.ru/).
2.  Создайте новый клиент.
3.  **Права доступа:** Выберите `yandex:avatar:read`, `login:email`, `login:info` и т.д.
4.  **Callback URL:** Вам понадобится URL обратного вызова Keycloak (см. ниже).
    *   Формат: `http://<хост-keycloak>/realms/<имя-realm>/broker/yandex/endpoint`
5.  Сохраните `Client ID` и `Client Secret`.

## 2. Настройка Identity Provider в Keycloak
1.  **Войдите в консоль администратора Keycloak.**
2.  **Перейдите в Identity Providers.**
3.  **Добавить провайдера:** Выберите `User-defined` (OpenID Connect v1.0) или `Yandex` (если доступно в списке вашей версии Keycloak).
    *   *Примечание:* Стандартный OIDC часто работает лучше, если Яндекс отсутствует в списке предустановленных.
4.  **Конфигурация:**
    *   **Alias (Псевдоним):** `yandex`
    *   **Display Name (Отображаемое имя):** `Яндекс ID`
    *   **Authorization URL:** `https://oauth.yandex.ru/authorize`
    *   **Token URL:** `https://oauth.yandex.ru/token`
    *   **Client ID:** (Из шага 1)
    *   **Client Secret:** (Из шага 1)
    *   **Client Authentication:** `Client secret sent as post` (обычно).
5.  **Mappers (Мапперы) (Необязательно, но рекомендуется):**
    *   Сопоставьте `email` с `user.email`.
    *   Сопоставьте `first_name`, `last_name`.
6.  **Сохранить.**

## 3. Тестирование
1.  Перейдите на страницу входа в приложение.
2.  Вы должны увидеть кнопку "Яндекс ID".
3.  Нажатие на нее перенаправляет в Яндекс.
4.  После авторизации Яндекс перенаправляет обратно в Keycloak.
5.  **Профиль пользователя:** Keycloak предложит пользователю просмотреть/обновить свой профиль (First Login Flow), если не настроено "Auto Link" (Автоматическое связывание).
6.  **Сохранение данных:** Профиль пользователя сохраняется в базе данных Keycloak.
