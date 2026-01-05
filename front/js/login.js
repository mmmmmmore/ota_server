// Minimal client-side logic
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const errorEl = document.getElementById('error');

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    errorEl.textContent = '';

    const data = new FormData(form);
    const payload = {
      email: data.get('email'),
      password: data.get('password'),
    };

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // Include credentials if server sets a cookie on the same origin
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        // Server is expected to set an HttpOnly cookie; then we can redirect.
        window.location.href = '/ota-management';
      } else if (res.status === 401) {
        errorEl.textContent = 'Invalid credentials';
      } else {
        const text = await res.text();
        errorEl.textContent = text || 'Login failed';
      }
    } catch (err) {
      console.error(err);
      errorEl.textContent = 'Network error';
    }
  });
});