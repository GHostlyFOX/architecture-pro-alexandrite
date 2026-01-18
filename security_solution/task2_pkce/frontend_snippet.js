// Frontend Logic (Vue/React generic snippet)

// OLD WAY (Token in LocalStorage - REMOVE THIS)
/*
const token = localStorage.getItem('access_token');
axios.get('http://backend/api/orders', {
  headers: { Authorization: `Bearer ${token}` }
});
*/

// NEW WAY (Session Cookie handled by Browser)

// 1. Login is just a redirect
function login() {
  window.location.href = "http://bionicpro-auth-service:8000/login";
}

// 2. API Requests go to the BFF, no headers needed (cookie is automatic)
async function getOrders() {
  try {
    // Note: Request goes to the BFF (auth service), which proxies to the actual backend
    const response = await fetch('/api/orders', {
      method: 'GET',
      credentials: 'include' // Important! Sends the HttpOnly cookie
    });

    if (response.status === 401) {
      // Session expired or invalid
      login();
      return;
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch orders", error);
  }
}

// 3. Logout
async function logout() {
    await fetch('/logout', { method: 'POST' });
    window.location.reload();
}
