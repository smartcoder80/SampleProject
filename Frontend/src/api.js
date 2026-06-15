const BASE_URL = process.env.REACT_APP_API_URL

function authHeaders() {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function login(username, password) {
  const res = await fetch(`${BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Login failed')
  return data
}

export async function register(username, email, password) {
  const res = await fetch(`${BASE_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Registration failed')
  return data
}

export async function getMe() {
  const res = await fetch(`${BASE_URL}/me`, {
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Unauthorized')
  return data
}

export async function logout() {
  await fetch(`${BASE_URL}/logout`, {
    method: 'POST',
    headers: authHeaders(),
  })
  localStorage.removeItem('token')
  localStorage.removeItem('username')
}
