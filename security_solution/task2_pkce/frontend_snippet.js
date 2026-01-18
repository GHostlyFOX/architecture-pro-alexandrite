// Логика Фронтенда (Пример для Vue/React)

// СТАРЫЙ СПОСОБ (Токен в LocalStorage - УДАЛИТЬ ЭТО)
/*
const token = localStorage.getItem('access_token');
axios.get('http://backend/api/orders', {
  headers: { Authorization: `Bearer ${token}` }
});
*/

// НОВЫЙ СПОСОБ (Сессионная Cookie обрабатывается браузером)

// 1. Вход - это просто редирект
function login() {
  window.location.href = "http://bionicpro-auth-service:8000/login";
}

// 2. API-запросы идут на BFF, заголовки не нужны (cookie подставляется автоматически)
async function getOrders() {
  try {
    // Примечание: Запрос идет на BFF (auth service), который проксирует его на реальный бэкенд
    const response = await fetch('/api/orders', {
      method: 'GET',
      credentials: 'include' // Важно! Отправляет HttpOnly cookie
    });

    if (response.status === 401) {
      // Сессия истекла или недействительна
      login();
      return;
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Не удалось получить заказы", error);
  }
}

// 3. Выход
async function logout() {
    await fetch('/logout', { method: 'POST' });
    window.location.reload();
}
